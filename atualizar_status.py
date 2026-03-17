import sqlite3

conn = sqlite3.connect('banco.db')
try:
    conn.execute("ALTER TABLE marketplace ADD COLUMN status TEXT DEFAULT 'ativo'")
    print("Sucesso: Coluna de status adicionada ao Marketplace!")
except sqlite3.OperationalError as e:
    print("Aviso:", e)

conn.commit()
conn.close()