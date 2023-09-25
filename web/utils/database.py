import sqlite3

class Database:
  def __init__(self, conn):
    self.conn = conn
    
  def insert(self, nome, matricula, ocupacao):
    try:
      cursor = self.conn.cursor()
      sql = "INSERT INTO alunos (nome, matricula, ocupacao) VALUES (?, ?, ?)"
      cursor.execute(sql, (nome, matricula, ocupacao))
      self.conn.commit()
    except sqlite3.Error as err:
      print(err)
      
  def select(self):
    try:
      cursor = self.conn.cursor()
      cursor.execute("SELECT * FROM alunos")
      response = cursor.fetchall()
      
      return response
    except sqlite3.Error as err:
      print(err)
      
  def create_table(self):
    try:
      cursor = self.conn.cursor()
      cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alunos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, matricula TEXT NOT NULL, ocupacao TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """
      )
      self.conn.commit()
    except sqlite3.Error as err:
      print(err)