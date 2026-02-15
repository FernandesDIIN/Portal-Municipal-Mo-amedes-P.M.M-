import sqlite3

conn = sqlite3.connect('banco.db')

# 1. Adiciona a coluna de contagem na tabela de postagens
try:
    conn.execute('ALTER TABLE postagens ADD COLUMN upvotes INTEGER DEFAULT 0')
except:
    pass # Se der erro é porque a coluna já existe, ignoramos.

# 2. Cria a tabela de bloqueio (para impedir votos duplicados)
conn.execute('''
    CREATE TABLE IF NOT EXISTS postagens_upvotes (
        usuario_id INTEGER,
        postagem_id INTEGER,
        PRIMARY KEY (usuario_id, postagem_id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
        FOREIGN KEY (postagem_id) REFERENCES postagens (id)
    )
''')

conn.commit()
conn.close()
print("Sistema de Relevância e Upvotes ativado no banco de dados!")