import subprocess
import logging

logger = logging.getLogger(__name__)

class SystemdManager:
    @staticmethod
    def start_service(service_name: str):
        try:
            subprocess.run(["systemctl", "start", service_name], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start {service_name}: {e.stderr}")
            raise Exception(f"Failed to start {service_name}")

    @staticmethod
    def stop_service(service_name: str):
        try:
            subprocess.run(["systemctl", "stop", service_name], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop {service_name}: {e.stderr}")
            raise Exception(f"Failed to stop {service_name}")

    @staticmethod
    def is_active(service_name: str) -> bool:
        try:
            result = subprocess.run(["systemctl", "is-active", service_name], capture_output=True, text=True)
            return result.stdout.strip() == "active"
        except Exception as e:
            logger.error(f"Error checking status for {service_name}: {e}")
            return False
