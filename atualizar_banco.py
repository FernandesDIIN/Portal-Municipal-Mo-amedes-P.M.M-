import sqlite3

conn = sqlite3.connect('banco.db')
try:
    conn.execute('ALTER TABLE marketplace ADD COLUMN imagem1 TEXT')
    conn.execute('ALTER TABLE marketplace ADD COLUMN imagem2 TEXT')
    print("Colunas de imagens adicionadas ao Marketplace com sucesso!")
except sqlite3.OperationalError as e:
    print("Aviso:", e)

conn.commit()
conn.close()