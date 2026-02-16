import sqlite3

conn = sqlite3.connect('banco.db')

conn.execute('''
    CREATE TABLE IF NOT EXISTS avaliacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diretorio_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        nota INTEGER NOT NULL CHECK(nota >= 1 AND nota <= 5),
        comentario TEXT,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (diretorio_id) REFERENCES diretorio (id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
''')

conn.commit()
conn.close()
print("Tabela de Avaliações e Estrelas criada com sucesso!")