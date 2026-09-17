import threading
import json
import time
import random
from app.core.config import settings

KAFKA_BROKER = settings.KAFKA_BROKER
TOPIC_OUT = "ml-alerts"

RECENT_ALERTS = []
ALERTS_LOCK = threading.Lock()
KAFKA_ALERTS_CONNECTED = False

def alerts_consumer_loop():
    global KAFKA_ALERTS_CONNECTED
    from kafka import KafkaConsumer
    while True:
        try:
            consumer = KafkaConsumer(
                TOPIC_OUT,
                bootstrap_servers=[KAFKA_BROKER],
                group_id="ml-fastapi-recent-alerts",
                value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                auto_offset_reset='latest'
            )
            KAFKA_ALERTS_CONNECTED = True
            for message in consumer:
                data = message.value
                if isinstance(data, dict) and data.get("event", {}).get("kind") == "alert":
                    with ALERTS_LOCK:
                        RECENT_ALERTS.insert(0, data)
                        if len(RECENT_ALERTS) > 50:
                            RECENT_ALERTS.pop()
        except Exception as e:
            KAFKA_ALERTS_CONNECTED = False
            print(f"ML Alerts Consumer Error: {e}")
            time.sleep(10)

def generate_demo_alert(src_ip: str, sensor_name: str, score: float, offset_sec: int = 0) -> dict:
    ts = int((time.time() - offset_sec) * 1000)
    severity = 1 if score >= 0.95 else 2
    return {
        "@timestamp": ts,
        "agent_name": sensor_name,
        "event": {
            "kind": "alert",
            "module": "ml_agent",
            "dataset": "ml.anomaly",
            "severity": severity,
        },
        "source": {"ip": src_ip},
        "ml": {
            "model_type": "HalfSpaceTrees",
            "anomaly_score": round(score, 4)
        },
        "message": f"Выявлена сетевая аномалия. Score: {score:.2f}",
        "kibana_investigate_url": f"{settings.KIBANA_URL}/app/discover#/?_a=(query:(language:kuery,query:'source.ip:%22{src_ip}%22'))&_g=(time:(from:'now-15m',to:'now'))"
    }

def init_demo_alerts():
    """Заполняет ленту первичными реалистичными алертами при старте системы."""
    initial_alerts = [
        generate_demo_alert("192.168.10.45", "Sensor-Alpha", 0.98, offset_sec=75),
        generate_demo_alert("192.168.10.82", "Sensor-Alpha", 0.96, offset_sec=140),
        generate_demo_alert("192.168.20.104", "Sensor-Beta", 0.91, offset_sec=280),
        generate_demo_alert("10.100.4.15", "Sensor-Gamma", 0.89, offset_sec=420),
        generate_demo_alert("192.168.10.15", "Sensor-Alpha", 0.88, offset_sec=600),
    ]
    with ALERTS_LOCK:
        RECENT_ALERTS.extend(initial_alerts)

def demo_alerts_loop():
    """Фоновый генератор потоковых аномалий для активного ML-агента в DEMO_MODE."""
    global KAFKA_ALERTS_CONNECTED
    KAFKA_ALERTS_CONNECTED = True
    from app.infrastructure.mock_services import mock_ml_state

    sample_ips = [
        ("192.168.10.65", "Sensor-Alpha"),
        ("192.168.10.99", "Sensor-Alpha"),
        ("192.168.20.114", "Sensor-Beta"),
        ("192.168.20.201", "Sensor-Beta"),
        ("10.100.2.77", "Sensor-Gamma"),
        ("172.16.5.33", "Sensor-Alpha")
    ]

    while True:
        try:
            if mock_ml_state.is_active:
                src_ip, sensor = random.choice(sample_ips)
                score = round(random.uniform(0.86, 0.99), 4)
                alert = generate_demo_alert(src_ip, sensor, score)
                with ALERTS_LOCK:
                    RECENT_ALERTS.insert(0, alert)
                    if len(RECENT_ALERTS) > 50:
                        RECENT_ALERTS.pop()
        except Exception as e:
            print(f"[!] Ошибка в demo_alerts_loop: {e}")

        # Генерация нового алерта каждые 12–20 секунд при активном агенте
        time.sleep(random.randint(12, 20))

def start_alerts_consumer():
    if settings.DEMO_MODE:
        init_demo_alerts()
        t_demo = threading.Thread(target=demo_alerts_loop, daemon=True)
        t_demo.start()
    else:
        thread = threading.Thread(target=alerts_consumer_loop, daemon=True)
        thread.start()
