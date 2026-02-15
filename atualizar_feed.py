import sqlite3

conn = sqlite3.connect('banco.db')
try:
    # Adiciona a coluna 'fixado' na tabela de postagens (0 = normal, 1 = fixado no topo)
    conn.execute('ALTER TABLE postagens ADD COLUMN fixado INTEGER DEFAULT 0')
    conn.commit()
    print("Sucesso: O sistema de posts fixados foi ativado no banco de dados!")
except Exception as e:
    print(f"Aviso: A coluna já existe ou ocorreu um erro: {e}")
    
conn.close()