from app.core.config import settings
from app.infrastructure.mock_services import MockSSHClientAdapter

class SSHClientAdapter:
    def __init__(self):
        self.is_demo = settings.DEMO_MODE
        if self.is_demo:
            self._mock = MockSSHClientAdapter()

    def _get_client(self, ip: str):
        import paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, username=settings.SSH_USER, key_filename=settings.SSH_KEY_PATH, timeout=settings.SSH_TIMEOUT)
        return ssh

    def execute(self, ip: str, command: str) -> str:
        if self.is_demo:
            return self._mock.execute(ip, command)

        import time
        ssh = self._get_client(ip)
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            start_time = time.time()
            timeout = 10.0
            while not stdout.channel.exit_status_ready():
                if time.time() - start_time > timeout:
                    raise Exception("Превышено время ожидания выполнения команды SSH (10 сек)")
                time.sleep(0.1)
                
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            if exit_status != 0:
                raise Exception(f"SSH Error: {error}")
            return output
        finally:
            ssh.close()

    def download_file(self, ip: str, remote_path: str, local_path: str):
        if self.is_demo:
            return self._mock.download_file(ip, remote_path, local_path)

        ssh = self._get_client(ip)
        try:
            sftp = ssh.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
        finally:
            ssh.close()

    def upload_file(self, ip: str, local_path: str, remote_path: str):
        if self.is_demo:
            return self._mock.upload_file(ip, local_path, remote_path)

        ssh = self._get_client(ip)
        try:
            sftp = ssh.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
        finally:
            ssh.close()
