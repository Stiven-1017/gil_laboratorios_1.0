import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.user = os.getenv('DB_USER', 'gil_user')
        self.password = os.getenv('DB_PASSWORD', 'gil_password_2025')
        self.database = os.getenv('DB_NAME', 'gil_laboratorios')

class GILSystem:
    def __init__(self, config):
        self.config = config
        self.conn = None

    def test_connection(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.config.host,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                port=self.config.port
            )
            if self.conn.is_connected():
                print("✅ Conexión exitosa!")
                return True
            else:
                print("❌ Error en la conexión")
                return False
        except Exception as e:
            print(f"💥 Error: {e}")
            return False
        finally:
            if self.conn and self.conn.is_connected():
                self.conn.close()

# Clases mínimas para el script
class Usuario:
    pass

class Equipo:
    pass

class Prestamo:
    pass