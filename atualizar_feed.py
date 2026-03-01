import sqlite3

conn = sqlite3.connect('banco.db')
try:
    conn.execute('ALTER TABLE postagens ADD COLUMN imagem1 TEXT')
    conn.execute('ALTER TABLE postagens ADD COLUMN imagem2 TEXT')
    print("Sucesso: Colunas de imagens adicionadas ao Feed da Comunidade!")
except sqlite3.OperationalError as e:
    print("Aviso:", e)

conn.commit()
conn.close()