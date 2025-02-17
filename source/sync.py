import time
from sqlite3 import connect
from source.GLOBAL import PATHS
from datetime import datetime

def check_for_new_messages(username, friend, callback):
    SQL = connect(PATHS["database.db"])
    SQL_CURSOR = SQL.cursor()

    last_checked = datetime.now()
    while True:
        time.sleep(1)
        new_messages = SQL_CURSOR.execute(
            "SELECT * FROM Messages WHERE to_ = ? AND from_ = ?",
            (username, friend)
        ).fetchall()
        for message in new_messages:
            message_time = datetime.strptime(message[0], '%Y-%m-%d %H:%M.%S')
            if message_time > last_checked:
                callback(message)
                last_checked = datetime.now()