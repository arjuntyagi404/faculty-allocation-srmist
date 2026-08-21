import sqlite3, os
db='database.db'
if not os.path.exists(db):
    print('DATABASE_NOT_FOUND')
    raise SystemExit(0)
con=sqlite3.connect(db)
cur=con.cursor()
cur.execute("PRAGMA table_info('faculty')")
rows=cur.fetchall()
if not rows:
    print('TABLE_NOT_FOUND')
else:
    for r in rows:
        print(r)
con.close()
