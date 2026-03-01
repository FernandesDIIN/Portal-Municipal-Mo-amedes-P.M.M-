import sqlite3

conn = sqlite3.connect('banco.db')
try:
    conn.execute('ALTER TABLE galeria_diretorio ADD COLUMN titulo TEXT')
    print("Coluna 'titulo' adicionada à galeria do diretório com sucesso!")
except sqlite3.OperationalError as e:
    print("Aviso:", e)

conn.commit()
conn.close()