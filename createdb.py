import sqlite3

conn = sqlite3.connect('database.db')
print("Opened database successfully")

conn.execute('CREATE TABLE report (personnel TEXT, starttime DATETIME, endtime DATETIME, client TEXT, section TEXT, patient TEXT, country TEXT, summary TEXT)')
print("Table created successfully")
conn.close()




"""
# To delete record from python shell
>>> import sqlite3
>>> conn = sqlite3.connect("database.db")
>>> conn.execute("DELETE FROM report WHERE starttime = '2018-02-01T12:12';")
<sqlite3.Cursor object at 0x10a69d650>
>>> conn.commit()
>>> conn.close()

"""