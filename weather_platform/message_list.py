import sqlite3

# 1. connect DB
DATABASE_FILE = 'weather_platform.db'
dbc = sqlite3.connect(DATABASE_FILE)
cursor = dbc.cursor()

# 2. execute SQL script
scriptSQL = '''
        SELECT * FROM messages
    '''
cursor.execute(scriptSQL)
#dbc.commit()
results = cursor.fetchall() #SELECT query
print('messages fetched successfully')
print(results)

# 3. close connection
dbc.close()