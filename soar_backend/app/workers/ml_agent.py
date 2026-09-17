import json
import time
import os
import pickle
import argparse
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from kafka import KafkaConsumer, KafkaProducer
from river import anomaly, compose, preprocessing

# Конфигурация
KAFKA_BROKER = "10.0.0.10:9092"
TOPIC_IN = "zeek-events"
TOPIC_OUT = "ml-alerts"
STATE_FILE = "/opt/soar_backend/models/ml_state.pkl"

# --- СТАНДАРТНЫЕ ПАРАМЕТРЫ ИЗ СТАТЬИ HS-TREES ---
N_TREES = 25
MAX_DEPTH = 15
WINDOW_SIZE = 250
ANOMALY_THRESHOLD = 0.85

def create_pipeline():
    """Создает эталонный пайплайн ML по статье S.C. Tan et al."""
    return compose.Pipeline(
        preprocessing.MinMaxScaler(),
        anomaly.HalfSpaceTrees(
            n_trees=N_TREES,
            height=MAX_DEPTH,
            window_size=WINDOW_SIZE,
            seed=42
        )
    )

def load_state():
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "rb") as f:
                state = pickle.load(f)
                models = defaultdict(create_pipeline, state.get("models", {}))
                print(f"[*] Успешно загружен профиль нормы для сенсоров: {list(models.keys())}")
                return models
        except Exception as e:
            print(f"[!] Ошибка загрузки состояния: {e}")
    return defaultdict(create_pipeline)

def save_state(models):
    try:
        with open(STATE_FILE, "wb") as f:
            pickle.dump({"models": dict(models)}, f)
        print(f"\n[*] Модель успешно сохранена в {STATE_FILE}")
    except Exception as e:
        print(f"\n[!] Ошибка при сохранении: {e}")

def generate_kibana_link(src_ip: str, event_ts: float) -> str:
    """Генерирует ссылку на Kibana строго вокруг времени самого события (+/- 5 минут)"""
    dt_center = datetime.datetime.utcfromtimestamp(event_ts)
    dt_from = dt_center - datetime.timedelta(minutes=5)
    dt_to = dt_center + datetime.timedelta(minutes=5)
    
    str_from = dt_from.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
    str_to = dt_to.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
    
    base_url = "http://10.0.0.20:5601/app/discover#/"
    # ИСПОЛЬЗУЕМ %22 ВМЕСТО \"
    query = f"?_a=(query:(language:kuery,query:'source.ip:%22{src_ip}%22'))"
    timerange = f"&_g=(time:(from:'{str_from}',to:'{str_to}'))"
    return f"{base_url}{query}{timerange}"

def process_message(event, mode, models, model_locks, producer, count_dict, count_lock):
    if event.get("log_type") != "conn":
        return
        
    agent_name = event.get("agent_name", "unknown_sensor")
    src_ip = event.get("id.orig_h")
    zeek_ts = float(event.get("ts", time.time()))
    
    if not src_ip: return

    features = {
        "duration": float(event.get("duration", 0.0)),
        "orig_bytes": float(event.get("orig_bytes", 0.0)),
        "resp_bytes": float(event.get("resp_bytes", 0.0)),
        "orig_pkts": float(event.get("orig_pkts", 0.0)),
        "resp_pkts": float(event.get("resp_pkts", 0.0)),
    }

    # Берем лок для конкретного сенсора
    with model_locks[agent_name]:
        model = models[agent_name]
        with count_lock:
            count_dict['total'] += 1
            current_count = count_dict['total']
        
        if mode == 'train':
            model.learn_one(features)
            if current_count % 1000 == 0:
                print(f"[{agent_name}] Обработано для базового профиля: {current_count} соединений...")
        
        elif mode == 'detect':
            anomaly_score = model.score_one(features)
            model.learn_one(features)

            if anomaly_score >= ANOMALY_THRESHOLD:
                print(f"[!!!] АНОМАЛИЯ ({anomaly_score:.2f}) на {agent_name} от {src_ip}")
                
                alert_event = {
                    "@timestamp": int(time.time() * 1000),
                    "agent_name": agent_name,
                    "event": {
                        "kind": "alert",
                        "module": "ml_agent",
                        "dataset": "ml.anomaly",
                        "severity": 1 if anomaly_score >= 0.95 else 2,
                    },
                    "source": {"ip": src_ip},
                    "ml": {
                        "model_type": "HalfSpaceTrees", 
                        "anomaly_score": round(anomaly_score, 4)
                    },
                    "message": f"Выявлена сетевая аномалия. Score: {anomaly_score:.2f}",
                    "kibana_investigate_url": generate_kibana_link(src_ip, zeek_ts)
                }
                # producer.send потокобезопасен в библиотеке kafka-python
                producer.send(TOPIC_OUT, value=alert_event)

def run_ml_agent(mode: str):
    print(f"[*] Инициализация ML-агента. Режим: {mode.upper()}")
    print(f"[*] Параметры: t={N_TREES}, h={MAX_DEPTH}, psi={WINDOW_SIZE}")
    print("[*] Включена многопоточная обработка.")
    
    models = load_state() if mode == 'detect' else defaultdict(create_pipeline)
    model_locks = defaultdict(threading.Lock)
    count_dict = {'total': 0}
    count_lock = threading.Lock()
    
    offset_reset = 'earliest' if mode == 'train' else 'latest'
    
    consumer = KafkaConsumer(
        TOPIC_IN,
        bootstrap_servers=[KAFKA_BROKER],
        group_id=f"ml-agent-{mode}",
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset=offset_reset
    )
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    print("[*] Ожидание потока данных... (Нажмите Ctrl+C для завершения)")

    try:
        # Используем ThreadPoolExecutor для параллельной обработки
        with ThreadPoolExecutor(max_workers=8) as executor:
            for message in consumer:
                event = message.value
                # Отправляем задачу в пул потоков
                executor.submit(
                    process_message,
                    event, mode, models, model_locks, producer, count_dict, count_lock
                )
    except KeyboardInterrupt:
        if mode == 'train':
            save_state(models)
        else:
            print("\n[*] Завершение работы режима детектирования.")
    except Exception as e:
        print(f"\n[!] Ошибка выполнения: {e}")
    finally:
        consumer.close()
        producer.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ML Anomaly Detector")
    parser.add_argument('--mode', choices=['train', 'detect'], required=True, help="Режим работы: train (обучение) или detect (выявление)")
    args = parser.parse_args()
    
    run_ml_agent(args.mode)
