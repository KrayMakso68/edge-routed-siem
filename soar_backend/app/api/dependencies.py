from fastapi import Depends
from app.infrastructure.ssh_client import SSHClientAdapter
from app.services.sensor_service import SensorService
from app.services.rule_service import RuleService
from app.services.pcap_service import PcapService
from app.services.rule_source_service import RuleSourceService

def get_ssh_client() -> SSHClientAdapter: return SSHClientAdapter()
def get_sensor_service() -> SensorService: return SensorService()
def get_rule_service(ssh: SSHClientAdapter = Depends(get_ssh_client)) -> RuleService: return RuleService(ssh)
def get_pcap_service(ssh: SSHClientAdapter = Depends(get_ssh_client)) -> PcapService: return PcapService(ssh)
def get_rule_source_service() -> RuleSourceService: return RuleSourceService()
