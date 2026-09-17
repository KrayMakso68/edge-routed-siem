from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.infrastructure.database import init_db
from app.api.routers import sensors, rules, rule_sources, pcap, ml, vpn

init_db()
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensors.router)
app.include_router(rules.router)
app.include_router(rule_sources.router)
app.include_router(pcap.router)
app.include_router(ml.router)
app.include_router(vpn.router)

from app.core.telemetry import start_telemetry_consumer
from app.core.alerts_consumer import start_alerts_consumer

@app.on_event("startup")
def startup_event():
    start_telemetry_consumer()
    start_alerts_consumer()

@app.get("/health")
def health_check():
    return {"status": "ok", "architecture": "Clean/Onion"}

@app.get("/api/system/status")
def system_status():
    if settings.DEMO_MODE:
        return {"kafka_connected": True}
    import app.core.telemetry as telemetry
    import app.core.alerts_consumer as alerts_consumer
    return {
        "kafka_connected": telemetry.KAFKA_TELEMETRY_CONNECTED and alerts_consumer.KAFKA_ALERTS_CONNECTED
    }
