from app.infrastructure.ssh_client import SSHClientAdapter

class PcapService:
    def __init__(self, ssh_client: SSHClientAdapter):
        self.ssh_client = ssh_client

    def get_list(self, ip: str):
        # Ищем только .pcap файлы и игнорируем ошибки пустых директорий
        cmd = "cd /var/log/pcap 2>/dev/null && ls -lh *.pcap 2>/dev/null | awk '{print $9, $5, $6, $7}' || true"
        raw_output = self.ssh_client.execute(ip, cmd)
        files = []
        for line in raw_output.split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 4:
                    files.append({"filename": parts[0], "size": parts[1], "date": f"{parts[2]} {parts[3]}"})
        return files

    def download(self, ip: str, filename: str, local_path: str):
        remote_path = f"/var/log/pcap/{filename}"
        self.ssh_client.download_file(ip, remote_path, local_path)
