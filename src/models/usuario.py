import mysql.connector
from config import Config

class Usuario:
    def __init__(self):
        self.conn = mysql.connector.connect(
            
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def crear_usuario(self, documento, nombres, apellidos, email, password_hash, id_rol=4):
        sql = """
        INSERT INTO usuarios (documento, nombres, apellidos, email, password_hash, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (documento, nombres, apellidos, email, password_hash, id_rol))
        self.conn.commit()
        return self.cursor.lastrowid

    def autenticar(self, documento, password_hash):
        sql = "SELECT * FROM usuarios WHERE documento = %s AND password_hash = %s"
        self.cursor.execute(sql, (documento, password_hash))
        return self.cursor.fetchone()