import sqlite3

conn = sqlite3.connect('kanban.db')
print("Opened database successfully")

conn.execute('CREATE TABLE signup(uname TEXT, uemail TEXT, upassword TEXT)')
print("Table created successfully")
conn.close()