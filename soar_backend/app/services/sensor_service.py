from app.infrastructure.database import get_db_connection
from app.domain.schemas import SensorCreate, SensorUpdate

class SensorService:
    def get_all(self):
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM sensors").fetchall()
        conn.close()
        return [dict(ix) for ix in rows]

    def get_by_id(self, sensor_id: int):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM sensors WHERE id = ?", (sensor_id,)).fetchone()
        conn.close()
        if not row:
            raise Exception("Сенсор не найден в БД")
        return dict(row)

    def create(self, dto: SensorCreate):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sensors (name, ip, network, description) VALUES (?, ?, ?, ?)",
                       (dto.name, dto.ip, dto.network, dto.description))
        conn.commit()
        sensor_id = cursor.lastrowid
        conn.close()
        return self.get_by_id(sensor_id)

    def update(self, sensor_id: int, dto: SensorUpdate):
        current = self.get_by_id(sensor_id)
        name = dto.name if dto.name is not None else current['name']
        ip = dto.ip if dto.ip is not None else current['ip']
        network = dto.network if dto.network is not None else current['network']
        description = dto.description if dto.description is not None else current['description']
        conn = get_db_connection()
        conn.execute("UPDATE sensors SET name=?, ip=?, network=?, description=? WHERE id=?",
                     (name, ip, network, description, sensor_id))
        conn.commit()
        conn.close()
        return self.get_by_id(sensor_id)

    def delete(self, sensor_id: int):
        conn = get_db_connection()
        conn.execute("DELETE FROM sensors WHERE id = ?", (sensor_id,))
        conn.commit()
        conn.close()
