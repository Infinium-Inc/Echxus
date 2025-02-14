from secrypto import Key, encrypt, decrypt
from os.path import exists
from os import makedirs
from sqlite3 import connect

__seed = 4852572164214751712476216756
GLOBAL_KEY = Key(seed=__seed)

DIRECTORY = "C:\\Users\\Public\\AppData\\Echxus"
if not exists(DIRECTORY):
    makedirs(DIRECTORY)

PATHS = {
    "favicon.ico" : DIRECTORY+"\\assets\\icons\\favicon.ico",
    "database.db" : DIRECTORY+"\\database.db"
}

GLOBAL_SQL = connect(PATHS["database.db"])
GLOBAL_SQL.create_function("decrypt", 1, lambda x: decrypt(x, GLOBAL_KEY))
GLOBAL_SQL.create_function("encrypt", 1, lambda x: encrypt(x, GLOBAL_KEY))

SQL_CURSOR = GLOBAL_SQL.cursor()
SQL_CURSOR.execute("CREATE TABLE IF NOT EXISTS Users (username TEXT, name TEXT, password TEXT, seed TEXT)")
SQL_CURSOR.execute("CREATE TABLE IF NOT EXISTS Info (username TEXT, friends TEXT)")
SQL_CURSOR.execute("CREATE TABLE IF NOT EXISTS Messages (timestamp TEXT, from_ TEXT, message TEXT, to_ TEXT)")