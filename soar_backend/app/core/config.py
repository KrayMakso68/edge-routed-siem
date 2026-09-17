import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    class AppSettings(BaseSettings):
        PROJECT_NAME: str = "SIEM & SOAR Master API"
        VERSION: str = "4.0 (Enterprise)"
        DEMO_MODE: bool = True
        KAFKA_BROKER: str = "10.0.0.10:9092"
        KIBANA_URL: str = "http://localhost:5601"
        PKI_DIR: str = os.getenv("PKI_DIR", str(BASE_DIR / "data" / "openvpn-ca"))
        OPENVPN_SERVER: str = "root@10.0.0.1"
        SSH_USER: str = os.getenv("SSH_USER", "soc-operator")
        SSH_TIMEOUT: int = 5
        SSH_KEY_PATH: str = os.getenv("SSH_KEY_PATH", str(Path.home() / ".ssh" / "id_ed25519"))
        DB_PATH: str = os.getenv("DB_PATH", str(BASE_DIR / "data" / "soar.db"))

        model_config = SettingsConfigDict(
            env_file=str(BASE_DIR / ".env"),
            env_file_encoding="utf-8",
            extra="ignore"
        )
except ImportError:
    try:
        from pydantic import BaseSettings
        class AppSettings(BaseSettings):
            PROJECT_NAME: str = "SIEM & SOAR Master API"
            VERSION: str = "4.0 (Enterprise)"
            DEMO_MODE: bool = True
            KAFKA_BROKER: str = "10.0.0.10:9092"
            KIBANA_URL: str = "http://localhost:5601"
            PKI_DIR: str = os.getenv("PKI_DIR", str(BASE_DIR / "data" / "openvpn-ca"))
            OPENVPN_SERVER: str = "root@10.0.0.1"
            SSH_USER: str = os.getenv("SSH_USER", "soc-operator")
            SSH_TIMEOUT: int = 5
            SSH_KEY_PATH: str = os.getenv("SSH_KEY_PATH", str(Path.home() / ".ssh" / "id_ed25519"))
            DB_PATH: str = os.getenv("DB_PATH", str(BASE_DIR / "data" / "soar.db"))

            class Config:
                env_file = str(BASE_DIR / ".env")
                extra = "ignore"
    except ImportError:
        class AppSettings:
            def __init__(self):
                self.PROJECT_NAME = os.getenv("PROJECT_NAME", "SIEM & SOAR Master API")
                self.VERSION = os.getenv("VERSION", "4.0 (Enterprise)")
                self.DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() in ("true", "1", "yes")
                self.KAFKA_BROKER = os.getenv("KAFKA_BROKER", "10.0.0.10:9092")
                self.KIBANA_URL = os.getenv("KIBANA_URL", "http://localhost:5601")
                self.PKI_DIR = os.getenv("PKI_DIR", str(BASE_DIR / "data" / "openvpn-ca"))
                self.OPENVPN_SERVER = os.getenv("OPENVPN_SERVER", "root@10.0.0.1")
                self.SSH_USER = os.getenv("SSH_USER", "soc-operator")
                self.SSH_TIMEOUT = int(os.getenv("SSH_TIMEOUT", "5"))
                self.SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", str(Path.home() / ".ssh" / "id_ed25519"))
                self.DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "data" / "soar.db"))

settings = AppSettings()
