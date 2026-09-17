import threading
import json
import time
import random
from app.core.config import settings

KAFKA_BROKER = settings.KAFKA_BROKER
METRICS_TOPIC = "sensor-metrics"

# Глобальный словарь для хранения метрик:
# { "sensor_name": { "cpu": "12.5", "ram": "45.1", "last_seen": 1690000000.0 } }
SENSOR_METRICS = {}
KAFKA_TELEMETRY_CONNECTED = False

def consumer_loop():
    global KAFKA_TELEMETRY_CONNECTED
    from kafka import KafkaConsumer
    while True:
        try:
            print(f"[*] Запуск Kafka consumer для телеметрии ({METRICS_TOPIC})...")
            consumer = KafkaConsumer(
                METRICS_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                group_id="soar-telemetry-group",
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest'
            )
            KAFKA_TELEMETRY_CONNECTED = True
            for message in consumer:
                data = message.value
                sensor_name = data.get("agent_name")
                if not sensor_name:
                    continue
                    
                cpu = data.get("cpu_percent", 0.0)
                ram = data.get("ram_percent", 0.0)
                    
                SENSOR_METRICS[sensor_name] = {
                    "cpu": round(float(cpu), 1),
                    "ram": round(float(ram), 1),
                    "last_seen": time.time()
                }
        except Exception as e:
            KAFKA_TELEMETRY_CONNECTED = False
            print(f"[!] Ошибка в consumer_loop телеметрии: {e}")
            time.sleep(10)
        finally:
            if 'consumer' in locals():
                consumer.close()

def active_check_loop():
    from app.services.sensor_service import SensorService
    from app.infrastructure.ssh_client import SSHClientAdapter
    
    sensor_service = SensorService()
    ssh_client = SSHClientAdapter()
    
    while True:
        try:
            sensors = sensor_service.get_all()
            for s in sensors:
                name = s.get('name')
                ip = s.get('ip')
                if not name or not ip:
                    continue
                try:
                    cmd_metrics = "CPU=$(vmstat 1 2 | tail -n 1 | awk '{print 100 - $15}'); RAM=$(awk '/MemTotal/ {t=$2} /MemAvailable/ {a=$2} /MemFree/ {f=$2} /Buffers/ {b=$2} /Cached/ {c=$2} END {if(a>0) print (1-a/t)*100; else print (1-(f+b+c)/t)*100}' /proc/meminfo); echo \"$CPU $RAM\""
                    res_metrics = ssh_client.execute(ip, cmd_metrics)
                    parts = res_metrics.split()
                    
                    try:
                        cpu = round(float(parts[0]), 1) if len(parts) > 0 else 0.0
                    except ValueError:
                        cpu = 0.0
                        
                    try:
                        ram = round(float(parts[1]), 1) if len(parts) > 1 else 0.0
                    except ValueError:
                        ram = 0.0
                    
                    SENSOR_METRICS[name] = {
                        "cpu": cpu,
                        "ram": ram,
                        "last_seen": time.time()
                    }
                except Exception:
                    pass
        except Exception as e:
            print(f"[!] Ошибка в активной проверке сенсоров: {e}")
        time.sleep(5)

def demo_telemetry_loop():
    """Фоновая генерация реалистичной телеметрии сенсоров для DEMO_MODE."""
    global KAFKA_TELEMETRY_CONNECTED
    KAFKA_TELEMETRY_CONNECTED = True
    from app.services.sensor_service import SensorService

    sensor_service = SensorService()
    while True:
        try:
            sensors = sensor_service.get_all()
            for s in sensors:
                name = s.get('name')
                if not name:
                    continue
                # Реалистичные колебания нагрузки
                base_cpu = 6.0 if "Alpha" in name else (12.0 if "Beta" in name else 18.0)
                base_ram = 24.0 if "Alpha" in name else (31.0 if "Beta" in name else 42.0)
                
                cpu = round(base_cpu + random.uniform(-2.5, 4.0), 1)
                ram = round(base_ram + random.uniform(-1.0, 2.5), 1)
                
                SENSOR_METRICS[name] = {
                    "cpu": max(1.0, min(100.0, cpu)),
                    "ram": max(1.0, min(100.0, ram)),
                    "last_seen": time.time()
                }
        except Exception as e:
            print(f"[!] Ошибка в demo_telemetry_loop: {e}")
        time.sleep(3)

def start_telemetry_consumer():
    if settings.DEMO_MODE:
        t_demo = threading.Thread(target=demo_telemetry_loop, daemon=True)
        t_demo.start()
    else:
        t = threading.Thread(target=consumer_loop, daemon=True)
        t.start()
        t_check = threading.Thread(target=active_check_loop, daemon=True)
        t_check.start()
