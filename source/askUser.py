from sqlite3 import  Connection
from ast import literal_eval
from customtkinter import *
from pywinstyles import  *

DIRECTORY = f"C:\\Users\\Public\\AppData\\Echxus"

SQL = Connection(DIRECTORY+"\\database.db")
SQL_CURSOR = SQL.cursor()

PATHS = {
    "favicon.ico" : f"{DIRECTORY}\\assets\\icons\\favicon.ico",
}

def getAvailable(user) -> set[str]:
    users = SQL_CURSOR.execute("SELECT username FROM Users").fetchall()
    users = set([i[0] for i in users])

    friends = SQL_CURSOR.execute("SELECT friends FROM Info WHERE username = ?", (user, )).fetchone()
    friends = set(literal_eval(friends[0]))

    users.remove(user)
    users = users - friends

    return users


class Ask(CTkToplevel):

    def __init__(branch, username) -> None:
        available = getAvailable(username)
        if available == set(): return

        super().__init__(fg_color="#202020")
        branch.geometry("400x300")
        branch.after(200, lambda: branch.iconbitmap(PATHS["favicon.ico"]))
        branch.after(200, lambda: branch.focus())
        branch.title("Echxus | Add Friend")

        branch.out = StringVar()

        change_header_color(branch, "#202020")
        change_border_color(branch, "#202020")

        branch.searchVar = StringVar()
        branch.searchBar = CTkEntry(
            branch,
            fg_color="#2c2c2c",
            border_color="#3a3a3a",
            font=("JetBrains Mono Bold", 20),
            textvariable=branch.searchVar
        )
        branch.searchBar.place(relx=0.5, rely=0.1, anchor="center", relwidth=0.9)

        branch.userArray = []
        branch.userList = CTkScrollableFrame(branch, fg_color="#3a3a3a")
        branch.userList.place(relx=0.5, rely=0.575, anchor="center", relwidth=0.9, relheight=0.75)

        for i in available:
            branch.userArray.append(
                CTkButton(
                    branch.userList,
                    fg_color="#373737",
                    text=i,
                    hover_color="#808080",
                    font=("JetBrains Mono Medium", 20),
                    command=lambda: branch.set(i)
                )
            )
            branch.userArray[-1].pack(pady=5, fill="x", padx=2)

    def set(branch, setter) -> None:
        branch.out.set(setter)
        branch.destroy()

    def __str__(branch) -> str:
        return branch.out.get()