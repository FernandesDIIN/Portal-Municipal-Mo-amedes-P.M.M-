import sqlite3

connection = sqlite3.connect('banco.db')

with open('schema.sql', 'r', encoding='utf-8') as f:
    connection.executescript(f.read())

connection.commit()
connection.close()

print("Banco de dados 'banco.db' criado e inicializado com sucesso!")
