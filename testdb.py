import sqlite3

conn = sqlite3.connect('kanban.db')
print("Opened database successfully")

cur = conn.cursor() 
cur.execute( "select * from card natural join list where uemail=? and list_title=?",("dikshant@gmail.com","todo"))
list=cur.fetchall()
print(list)
conn.commit()
conn.close()