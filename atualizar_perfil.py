import sqlite3

conn = sqlite3.connect('banco.db')

conn.execute('''
    CREATE TABLE IF NOT EXISTS galeria_usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        nome_imagem TEXT NOT NULL,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
''')

conn.commit()
conn.close()
print("Tabela do Memorial e Perfil criada com sucesso!")