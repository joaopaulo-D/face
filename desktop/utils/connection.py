import sqlite3

def sqliteConnect():
    try:
        conn = sqlite3.connect('../face_ic.db', check_same_thread=False)
    except sqlite3.Error as err:
        print("Erro ao conectar ao banco de dados:", err)
        conn = None
    return conn