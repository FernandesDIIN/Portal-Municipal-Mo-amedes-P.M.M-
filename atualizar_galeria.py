import sqlite3

conn = sqlite3.connect('banco.db')

# Cria a tabela para a Galeria Oficial do Município
conn.execute('''
    CREATE TABLE IF NOT EXISTS galeria_municipio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        local TEXT NOT NULL,
        nome_imagem TEXT NOT NULL,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()
print("Tabela da Galeria Global criada com sucesso!")