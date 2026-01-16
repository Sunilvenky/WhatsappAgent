import sqlite3

conn = sqlite3.connect('whatsapp_agent.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print('✅ Database Tables Created:')
for i, table in enumerate(tables, 1):
    print(f'{i:2d}. {table[0]}')

print(f'\nTotal: {len(tables)} tables')
conn.close()
