import os
import subprocess
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.core.config import settings
from app.infrastructure.mock_services import mock_pki_manager

router = APIRouter(prefix="/api/vpn", tags=["VPN"])

class VpnCreateRequest(BaseModel):
    name: str

class VpnRevokeRequest(BaseModel):
    name: str

@router.get("/certs")
def list_certs():
    if settings.DEMO_MODE:
        return mock_pki_manager.list_certs()

    index_file = os.path.join(settings.PKI_DIR, "pki", "index.txt")
    if not os.path.exists(index_file):
        return []
    
    certs = []
    with open(index_file, "r") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 6:
                status = parts[0]  # V (Valid) или R (Revoked)
                name = parts[5].split("CN=")[-1]
                if name not in ["ca", "server"]:
                    certs.append({
                        "name": name,
                        "status": "Valid" if status == "V" else "Revoked",
                        "serial": parts[3]
                    })
    return certs

@router.post("/create")
def create_vpn_client(req: VpnCreateRequest):
    if settings.DEMO_MODE:
        ovpn_file = mock_pki_manager.create_cert(req.name)
        return FileResponse(path=ovpn_file, filename=f"{req.name}.ovpn")

    # 1. Запуск easyrsa build-client-full <name> nopass
    try:
        env = os.environ.copy()
        env["EASYRSA_BATCH"] = "1"
        subprocess.run(
            ["./easyrsa", "build-client-full", req.name, "nopass"],
            cwd=settings.PKI_DIR,
            check=True,
            capture_output=True,
            text=True,
            env=env
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {e.stderr or e.stdout}")

    # 2. Сборка ovpn файла
    pki_dir = os.path.join(settings.PKI_DIR, "pki")
    ca_path = os.path.join(pki_dir, "ca.crt")
    cert_path = os.path.join(pki_dir, "issued", f"{req.name}.crt")
    key_path = os.path.join(pki_dir, "private", f"{req.name}.key")
    ta_path = os.path.join(settings.PKI_DIR, "ta.key")

    def read_file(path):
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        return ""

    ca_content = read_file(ca_path)
    cert_content = read_file(cert_path)
    if "-----BEGIN CERTIFICATE-----" in cert_content:
        cert_content = "-----BEGIN CERTIFICATE-----" + cert_content.split("-----BEGIN CERTIFICATE-----")[1]
    
    key_content = read_file(key_path)
    ta_content = read_file(ta_path)

    ovpn_template = f"""client
dev tun
proto udp
remote vpn-gateway.internal 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-GCM
verb 3

<ca>
{ca_content}
</ca>

<cert>
{cert_content}
</cert>

<key>
{key_content}
</key>

<tls-crypt>
{ta_content}
</tls-crypt>
"""
    output_dir = "/tmp/ovpn_profiles"
    if os.name == 'nt':
        output_dir = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'ovpn_profiles')
    os.makedirs(output_dir, exist_ok=True)
    ovpn_file = os.path.join(output_dir, f"{req.name}.ovpn")
    
    with open(ovpn_file, "w") as f:
        f.write(ovpn_template)
        
    return FileResponse(path=ovpn_file, filename=f"{req.name}.ovpn")

@router.post("/revoke")
def revoke_vpn_client(req: VpnRevokeRequest):
    if settings.DEMO_MODE:
        mock_pki_manager.revoke_cert(req.name)
        return {"status": "success", "message": f"Client {req.name} revoked"}

    try:
        env = os.environ.copy()
        env["EASYRSA_BATCH"] = "1"
        subprocess.run(
            ["./easyrsa", "revoke", req.name],
            cwd=settings.PKI_DIR,
            input="yes\n",
            text=True,
            check=True,
            capture_output=True,
            env=env
        )
        subprocess.run(
            ["./easyrsa", "gen-crl"],
            cwd=settings.PKI_DIR,
            check=True,
            capture_output=True,
            env=env
        )
        crl_path = os.path.join(settings.PKI_DIR, "pki", "crl.pem")
        subprocess.run(
            ["scp", "-i", settings.SSH_KEY_PATH, "-o", "StrictHostKeyChecking=no", crl_path, f"{settings.OPENVPN_SERVER}:/etc/openvpn/server/"],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка отзыва: {e.stderr or e.stdout}")
        
    return {"status": "success", "message": f"Client {req.name} revoked"}

@router.get("/download/{name}")
def download_vpn_client(name: str):
    if settings.DEMO_MODE:
        ovpn_file = mock_pki_manager.get_ovpn_profile(name)
        return FileResponse(path=ovpn_file, filename=f"{name}.ovpn")

    pki_dir = os.path.join(settings.PKI_DIR, "pki")
    ca_path = os.path.join(pki_dir, "ca.crt")
    cert_path = os.path.join(pki_dir, "issued", f"{name}.crt")
    key_path = os.path.join(pki_dir, "private", f"{name}.key")
    ta_path = os.path.join(settings.PKI_DIR, "ta.key")

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        raise HTTPException(status_code=404, detail="Сертификат не найден")

    def read_file(path):
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        return ""

    ca_content = read_file(ca_path)
    cert_content = read_file(cert_path)
    if "-----BEGIN CERTIFICATE-----" in cert_content:
        cert_content = "-----BEGIN CERTIFICATE-----" + cert_content.split("-----BEGIN CERTIFICATE-----")[1]
    
    key_content = read_file(key_path)
    ta_content = read_file(ta_path)

    ovpn_template = f"""client
dev tun
proto udp
remote vpn-gateway.internal 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-GCM
verb 3

<ca>
{ca_content}
</ca>

<cert>
{cert_content}
</cert>

<key>
{key_content}
</key>

<tls-crypt>
{ta_content}
</tls-crypt>
"""
    output_dir = "/tmp/ovpn_profiles"
    if os.name == 'nt':
        output_dir = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'ovpn_profiles')
    os.makedirs(output_dir, exist_ok=True)
    ovpn_file = os.path.join(output_dir, f"{name}.ovpn")
    with open(ovpn_file, "w") as f:
        f.write(ovpn_template)
        
    return FileResponse(path=ovpn_file, filename=f"{name}.ovpn")
