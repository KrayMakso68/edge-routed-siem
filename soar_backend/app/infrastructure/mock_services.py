import os
import time
import struct
import random
import uuid
from typing import List, Dict, Any
from app.core.config import settings

# ---------------------------------------------------------------------
# 1. In-memory Mock State Stores
# ---------------------------------------------------------------------

class MockRuleStore:
    """Хранилище пользовательских правил Suricata для каждого сенсора."""
    def __init__(self):
        self.rules_by_ip: Dict[str, List[str]] = {}

    def get_rules(self, ip: str) -> List[str]:
        if ip not in self.rules_by_ip:
            self.rules_by_ip[ip] = [
                'alert tcp any any -> $HOME_NET 22 (msg:"ET SCAN Potential SSH Brute Force"; flags:S; threshold:type both, track by_src, count 5, seconds 60; sid:2001219; rev:1;)',
                'alert http any any -> $HOME_NET any (msg:"ET WEB_SERVER Possible SQL Injection Attempt (UNION SELECT)"; content:"UNION"; nocase; content:"SELECT"; nocase; sid:2000001; rev:2;)',
                'alert tcp any any -> $HOME_NET [80,443] (msg:"ET ATTACK_RESPONSE Metasploit Meterpreter Reverse HTTPS Certificate"; content:"|16 03 01|"; sid:2020001; rev:1;)',
                'alert dns any any -> any any (msg:"ET DNS Query for Suspicious TLD (.top)"; dns.query; content:".top"; endswith; sid:2025110; rev:1;)',
                'alert icmp any any -> $HOME_NET any (msg:"ET SCAN Suspicious ICMP Ping Sweep"; itype:8; threshold:type both, track by_src, count 20, seconds 10; sid:2100342; rev:1;)'
            ]
        return self.rules_by_ip[ip]

    def add_rule(self, ip: str, rule: str):
        rules = self.get_rules(ip)
        rule_clean = rule.strip()
        if rule_clean and rule_clean not in rules:
            rules.append(rule_clean)

    def delete_rule(self, ip: str, rule: str):
        rules = self.get_rules(ip)
        rule_clean = rule.strip()
        if rule_clean in rules:
            rules.remove(rule_clean)

    def batch_delete(self, ip: str, rule_texts: List[str]):
        rules = self.get_rules(ip)
        del_set = set(r.strip() for r in rule_texts)
        self.rules_by_ip[ip] = [r for r in rules if r.strip() not in del_set]

    def set_rules(self, ip: str, new_rules: List[str]):
        self.rules_by_ip[ip] = [r.strip() for r in new_rules if r.strip()]

mock_rule_store = MockRuleStore()


class MockPKIManager:
    """Мок-менеджер инфраструктуры открытых ключей (Easy-RSA)."""
    def __init__(self):
        self.certs: List[Dict[str, str]] = [
            {"name": "Sensor-Alpha", "status": "Valid", "serial": "B12F86F43A6B6A899BD2269183A194B3"},
            {"name": "Sensor-Beta", "status": "Valid", "serial": "D89F41DA4F18DB69DB7D08178DA7CAD7"},
            {"name": "Gateway-DMZ", "status": "Valid", "serial": "E53A229F89B214C012EA89172B8CA102"},
            {"name": "Legacy-Sensor-01", "status": "Revoked", "serial": "AA1827C90812EA7716DF991823AB0192"}
        ]

    def list_certs(self) -> List[Dict[str, str]]:
        return list(self.certs)

    def create_cert(self, name: str) -> str:
        # Проверяем, существует ли уже такой сертификат
        for c in self.certs:
            if c["name"] == name:
                c["status"] = "Valid"
                return self._generate_ovpn(name)

        new_serial = uuid.uuid4().hex.upper()
        self.certs.append({
            "name": name,
            "status": "Valid",
            "serial": new_serial
        })
        return self._generate_ovpn(name)

    def revoke_cert(self, name: str):
        for c in self.certs:
            if c["name"] == name:
                c["status"] = "Revoked"
                return True
        return False

    def get_ovpn_profile(self, name: str) -> str:
        return self._generate_ovpn(name)

    def _generate_ovpn(self, name: str) -> str:
        output_dir = "/tmp/ovpn_profiles"
        if os.name == 'nt':
            output_dir = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'ovpn_profiles')
        os.makedirs(output_dir, exist_ok=True)
        ovpn_path = os.path.join(output_dir, f"{name}.ovpn")

        dummy_ca = "-----BEGIN CERTIFICATE-----\nMIIB/zCCAaegAwIBAgIU...\n[DEMO CA ROOT CERTIFICATE]\n-----END CERTIFICATE-----"
        dummy_cert = f"-----BEGIN CERTIFICATE-----\nMIIClDCCAXwCAQEwDQYJKoZIhvcNAQELBQA...\n[DEMO CERTIFICATE FOR {name.upper()}]\n-----END CERTIFICATE-----"
        dummy_key = "-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg...\n[DEMO PRIVATE KEY]\n-----END PRIVATE KEY-----"
        dummy_tls = "-----BEGIN OpenVPN Static key V1-----\n# 2048 bit OpenVPN TLS Crypt Key\n0123456789abcdef0123456789abcdef\n-----END OpenVPN Static key V1-----"

        content = f"""# Astra SOAR Generated OpenVPN Client Profile
client
dev tun
proto udp
remote vpn-gateway.internal 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-GCM
auth SHA256
verb 3

<ca>
{dummy_ca}
</ca>

<cert>
{dummy_cert}
</cert>

<key>
{dummy_key}
</key>

<tls-crypt>
{dummy_tls}
</tls-crypt>
"""
        with open(ovpn_path, "w", encoding="utf-8") as f:
            f.write(content)
        return ovpn_path

mock_pki_manager = MockPKIManager()


class MockMLState:
    """Управление состоянием ML-агента потокового анализа Half-Space Trees."""
    def __init__(self):
        self.is_active = True

    def start(self):
        self.is_active = True
        return {"status": "starting", "mode": "demo"}

    def stop(self):
        self.is_active = False
        return {"status": "stopping", "mode": "demo"}

    def get_status(self):
        return {"is_active": self.is_active}

mock_ml_state = MockMLState()


# ---------------------------------------------------------------------
# 2. Binary PCAP Generator (creates authentic pcap files for demo)
# ---------------------------------------------------------------------

def generate_synthetic_pcap(filepath: str, packet_count: int = 15):
    """
    Генерирует валидный бинарный файл формата libpcap с заголовками и пакетами TCP/UDP.
    Файл корректно открывается в Wireshark и tcpdump.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        # Global Header: magic, v_major, v_minor, thiszone, sigfigs, snaplen, network (1=Ethernet)
        global_header = struct.pack("=IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
        f.write(global_header)

        now = int(time.time()) - 300
        for i in range(packet_count):
            ts_sec = now + i * 2
            ts_usec = random.randint(1000, 999999)

            # Ethernet header (14 bytes): Dst MAC, Src MAC, EtherType (0x0800 IPv4)
            dst_mac = b'\x00\x0c\x29\x3e\x4f\x50'
            src_mac = b'\x00\x0c\x29\x6a\x7b\x8c'
            ethertype = b'\x08\x00'
            eth_header = dst_mac + src_mac + ethertype

            # IP header (20 bytes): IPv4, TCP (proto 6)
            src_ip_bytes = bytes([192, 168, 10, random.randint(10, 50)])
            dst_ip_bytes = bytes([10, 8, 0, 1])
            ip_header = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 60, random.randint(1, 65000), 0x4000, 64, 6, 0, src_ip_bytes, dst_ip_bytes)

            # TCP header (20 bytes): SYN or ACK
            sport = random.randint(1024, 65535)
            dport = random.choice([22, 80, 443, 8080, 9092])
            tcp_header = struct.pack("!HHIIBBHHH", sport, dport, random.randint(1000, 100000), 0, 0x50, 0x02, 64240, 0, 0)

            # Payload (16 bytes)
            payload = b"AstraSOAR_Trace_" + bytes([i])

            pkt_data = eth_header + ip_header + tcp_header + payload
            pkt_len = len(pkt_data)

            # Packet Header: ts_sec, ts_usec, incl_len, orig_len
            pkt_header = struct.pack("=IIII", ts_sec, ts_usec, pkt_len, pkt_len)
            f.write(pkt_header)
            f.write(pkt_data)


# ---------------------------------------------------------------------
# 3. Mock SSH Client Adapter
# ---------------------------------------------------------------------

class MockSSHClientAdapter:
    """
    Эмулятор SSH-клиента для автономного DEMO_MODE.
    Полностью воспроизводит выполнение команд сбора телеметрии,
    чтения и изменения правил Suricata, а также выгрузку дампов трафика PCAP.
    """
    def execute(self, ip: str, command: str) -> str:
        cmd = command.strip()

        # 1. Запрос телеметрии CPU и RAM
        if "CPU=" in cmd or "vmstat" in cmd or "/proc/meminfo" in cmd:
            cpu = round(random.uniform(5.4, 18.2), 1)
            ram = round(random.uniform(21.5, 36.8), 1)
            return f"{cpu} {ram}"

        # 2. Список файлов PCAP
        if "ls -lh *.pcap" in cmd or "ls -lh" in cmd:
            return (
                "traffic-2026-09-17_12.pcap 142M Sep 17 12:00\n"
                "traffic-2026-09-17_13.pcap 254M Sep 17 13:00\n"
                "traffic-2026-09-17_14.pcap 98M Sep 17 14:00\n"
                "traffic-2026-09-17_15.pcap 315M Sep 17 15:00\n"
                "traffic-2026-09-17_16.pcap 182M Sep 17 16:00"
            )

        # 3. Чтение правил Suricata (cat custom.rules)
        import re
        if re.search(r"\bcat\b", cmd) and "custom.rules" in cmd:
            rules = mock_rule_store.get_rules(ip)
            return "\n".join(rules)

        # 4. Добавление правила Suricata (echo '...' >> custom.rules)
        if "custom.rules" in cmd and ">>" in cmd:
            echo_idx = cmd.find("echo ")
            append_idx = cmd.find(">>", echo_idx)
            if echo_idx != -1 and append_idx != -1:
                raw_rule = cmd[echo_idx + 5 : append_idx].strip()
                if (raw_rule.startswith("'") and raw_rule.endswith("'")) or (raw_rule.startswith('"') and raw_rule.endswith('"')):
                    raw_rule = raw_rule[1:-1]
                new_rule = raw_rule.replace("'\\''", "'")
                mock_rule_store.add_rule(ip, new_rule)
            return '{"message": "done", "return": "OK"}'

        # 5. Удаление правила (grep -F -v ...)
        if "grep" in cmd and "custom.rules" in cmd:
            m = re.search(r"-x\s+['\"](.*?)['\"]", cmd)
            if m:
                del_rule = m.group(1).replace("'\\''", "'")
                mock_rule_store.delete_rule(ip, del_rule)
            return '{"message": "done", "return": "OK"}'

        # 6. Перезагрузка правил Suricata
        if "suricatasc" in cmd and "reload-rules" in cmd:
            return '{"message": "done", "return": "OK"}'

        # 7. Замена файла правил (mv ...)
        if "mv " in cmd and "custom.rules" in cmd:
            return '{"message": "done", "return": "OK"}'

        # Fallback
        return "OK"

    def download_file(self, ip: str, remote_path: str, local_path: str):
        if remote_path.endswith(".pcap"):
            generate_synthetic_pcap(local_path)
        else:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(f"# Simulated file content from {ip}:{remote_path}\n")

    def upload_file(self, ip: str, local_path: str, remote_path: str):
        if os.path.exists(local_path) and "custom.rules" in remote_path:
            with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            mock_rule_store.set_rules(ip, lines)
