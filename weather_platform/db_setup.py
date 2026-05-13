import sqlite3

#1. connect DB
DATABASE_FILE='project1.db'
dbc=sqlite3.connect(DATABASE_FILE)
cursor=dbc.cursor()

#2. execute SQL script
scriptSQL = '''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''

cursor.execute(scriptSQL)
dbc.commit()

print('messages table created successfully')

#3. close connection
dbc.close()