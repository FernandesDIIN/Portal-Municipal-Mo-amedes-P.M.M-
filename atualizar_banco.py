import sqlite3

# Conecta ao banco de dados existente
conn = sqlite3.connect('banco.db')

# Cria apenas a nova tabela de Galeria (se ela não existir)
conn.execute('''
    CREATE TABLE IF NOT EXISTS galeria_diretorio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diretorio_id INTEGER NOT NULL,
        nome_imagem TEXT NOT NULL,
        FOREIGN KEY (diretorio_id) REFERENCES diretorio (id)
    )
''')

conn.commit()
conn.close()
print("Tabela da Galeria criada com sucesso! Seus dados antigos estão a salvo.")