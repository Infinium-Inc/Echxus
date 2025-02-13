from sqlite3 import  Connection
from secrypto import Key, encrypt, decrypt
from os import path, makedirs
from datetime import datetime

DIRECTORY = f"C:\\Users\\Public\\AppData\\Echxus"
if not path.exists(DIRECTORY):
    makedirs(DIRECTORY)

GLOBAL_KEY = Key(seed=4852572164214751712476216756)

SQL = Connection(DIRECTORY+"\\database.db")
SQL_CURSOR = SQL.cursor()
SQL_CURSOR.execute("CREATE TABLE IF NOT EXISTS Messages (timestamp TEXT, from_ TEXT, message TEXT, to_ TEXT)")

def send(from_: str, message: str, to: str, fromPassword: str) -> None:
    if fromPassword != decrypt(SQL_CURSOR.execute("SELECT * FROM Users WHERE username = ?", (from_, )).fetchone()[2], GLOBAL_KEY):
        return
    seed = SQL_CURSOR.execute("SELECT * FROM Users WHERE username = ?", (to, )).fetchone()[3]
    SQL_CURSOR.execute("INSERT INTO Messages (timestamp, from_, message, to_) VALUES (?, ?, ?, ?)", (f'{datetime.now().date()} {datetime.now().hour}:{datetime.now().minute}.{datetime.now().second}', from_, encrypt(message, Key(seed=int(seed))), to))
    SQL.commit()

def get_messages(chat: str, password: str) -> list[str]:
    user1 = chat.split("-")[0]
    user2 = chat.split("-")[1]

    if password != decrypt(SQL_CURSOR.execute("SELECT * FROM Users WHERE username = ?", (user1, )).fetchone()[2], GLOBAL_KEY) and password != decrypt(SQL_CURSOR.execute("SELECT * FROM Users WHERE username = ?", (user2, )).fetchone()[2], GLOBAL_KEY):
        return []

    def toDate(total: str) -> datetime:
        item = total[0].split(" ")
        date = item[0].split("-")
        time = item[1].split(":")
        hour = time[0]
        time = time[1].split(".")
        return datetime(
            year=int(date[0]),
            month=int(date[1]),
            day=int(date[2]),
            hour=int(hour),
            minute=int(time[0]),
            second=int(time[1]),
        )

    query = """
    SELECT * FROM Messages
    WHERE (from_ = ? AND to_ = ?)
    OR (from_ = ? AND to_ = ?)
    """
    messages = sorted(SQL_CURSOR.execute(query, (user1, user2, user2, user1)).fetchall(), key=toDate)
    seed1 = int(SQL_CURSOR.execute("SELECT * FROM Users WHERE username = ?", (user1, )).fetchone()[3])
    seed2 = int(SQL_CURSOR.execute("SELECT * FROM Users WHERE username = ?", (user2, )).fetchone()[3])

    array = []

    for i in messages:
        message = decrypt(
            i[2],
            Key(seed=seed2 if i[1] == user1 else seed1)
        )
        array += [[i[0], i[1], message]]

    return array