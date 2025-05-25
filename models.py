import sqlite3

def init_db():
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS specimens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    specimen_id INTEGER,
                    file TEXT,
                    FOREIGN KEY (specimen_id) REFERENCES specimens(id)
                )''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()