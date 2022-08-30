import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (email, merchantID, apiKey, title, content) VALUES (?, ?, ?, ?, ?)",
            ('test1@email.com', "", "", 'First Post', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (email, merchantID, apiKey, title, content) VALUES (?, ?, ?, ?, ?)",
            ('test@email.com', "", "", 'Second Post', 'Content for the second post')
            )

connection.commit()
connection.close()
