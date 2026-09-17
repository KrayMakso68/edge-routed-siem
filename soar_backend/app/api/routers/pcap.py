import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.services.sensor_service import SensorService
from app.services.pcap_service import PcapService
from app.api.dependencies import get_pcap_service, get_sensor_service

router = APIRouter(prefix="/api/pcap", tags=["PCAP"])

@router.get("/list/{sensor_id}")
def list_pcaps(sensor_id: int, p_service: PcapService = Depends(get_pcap_service), s_service: SensorService = Depends(get_sensor_service)):
    try:
        sensor = s_service.get_by_id(sensor_id)
        return {"files": p_service.get_list(sensor['ip'])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{sensor_id}/{filename}")
def download_pcap(sensor_id: int, filename: str, background_tasks: BackgroundTasks, p_service: PcapService = Depends(get_pcap_service), s_service: SensorService = Depends(get_sensor_service)):
    try:
        sensor = s_service.get_by_id(sensor_id)
        temp_dir = "/tmp" if os.name != "nt" else tempfile.gettempdir()
        os.makedirs(temp_dir, exist_ok=True)
        local_path = os.path.join(temp_dir, filename)
        
        p_service.download(sensor['ip'], filename, local_path)
        background_tasks.add_task(lambda p: os.remove(p) if os.path.exists(p) else None, local_path)
        return FileResponse(path=local_path, filename=filename, media_type='application/vnd.tcpdump.pcap')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
