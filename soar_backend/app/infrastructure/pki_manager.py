import subprocess
from app.core.config import settings

class PKIManagerAdapter:
    """Адаптер для взаимодействия с bash-скриптами Easy-RSA."""
    
    def revoke_cert(self, sensor_name: str):
        subprocess.run(["./easyrsa", "--batch", "revoke", sensor_name], cwd=settings.PKI_DIR, check=True)
        
    def generate_crl(self):
        subprocess.run(["./easyrsa", "gen-crl"], cwd=settings.PKI_DIR, check=True)
        
    def push_crl_to_gateway(self, gateway_ip: str):
        subprocess.run(["scp", f"{settings.PKI_DIR}/pki/crl.pem", f"{settings.SSH_USER}@{gateway_ip}:/etc/openvpn/server/"], check=True)
