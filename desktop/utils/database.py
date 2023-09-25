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
      
  def consult(self, nome):
    try:
      cursor = self.conn.cursor()
      sql = "SELECT nome, matricula, ocupacao FROM alunos WHERE nome = ?"
      cursor.execute(sql, (nome,))
      response = cursor.fetchone()
      
      return response
    except sqlite3.Error as err:
      print(err)