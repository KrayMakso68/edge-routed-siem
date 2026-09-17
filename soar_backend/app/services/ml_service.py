import json
import logging
import time
from app.core.config import settings
from app.infrastructure.mock_services import mock_ml_state

logger = logging.getLogger(__name__)

ML_AGENT_SERVICE = "ml-agent"
KAFKA_BROKER = settings.KAFKA_BROKER
TOPIC_OUT = "ml-alerts"

class MLService:
    def start_agent(self):
        if settings.DEMO_MODE:
            return mock_ml_state.start()
        from app.infrastructure.systemd import SystemdManager
        SystemdManager.start_service(ML_AGENT_SERVICE)
        return {"status": "starting"}

    def stop_agent(self):
        if settings.DEMO_MODE:
            return mock_ml_state.stop()
        from app.infrastructure.systemd import SystemdManager
        SystemdManager.stop_service(ML_AGENT_SERVICE)
        return {"status": "stopping"}

    def get_status(self):
        if settings.DEMO_MODE:
            return mock_ml_state.get_status()
        from app.infrastructure.systemd import SystemdManager
        is_active = SystemdManager.is_active(ML_AGENT_SERVICE)
        return {"is_active": is_active}

    def alert_stream_generator(self):
        if settings.DEMO_MODE:
            from app.core.alerts_consumer import RECENT_ALERTS, ALERTS_LOCK
            last_idx = -1
            while True:
                with ALERTS_LOCK:
                    if RECENT_ALERTS and len(RECENT_ALERTS) > 0:
                        event_data = RECENT_ALERTS[0]
                        yield f"data: {json.dumps(event_data)}\n\n"
                time.sleep(5)
            return

        from kafka import KafkaConsumer
        try:
            consumer = KafkaConsumer(
                TOPIC_OUT,
                bootstrap_servers=[KAFKA_BROKER],
                group_id="ml-dashboard-stream",
                value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                auto_offset_reset='latest'
            )
            for message in consumer:
                if message.value:
                    event_data = message.value
                    if isinstance(event_data, dict) and event_data.get("event", {}).get("kind") == "alert":
                        yield f"data: {json.dumps(event_data)}\n\n"
        except Exception as e:
            logger.error(f"Kafka consumer error: {e}")
        finally:
            if 'consumer' in locals():
                consumer.close()
