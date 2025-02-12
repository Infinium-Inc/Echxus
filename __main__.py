from source import login, messaging, askUser
if not login.username: exit()
username = login.username

from customtkinter import *
from pywinstyles import *
from sqlite3 import  Connection
from ast import literal_eval

DIRECTORY = f"C:\\Users\\Public\\AppData\\Echxus"

SQL = Connection(DIRECTORY+"\\database.db")
SQL_CURSOR = SQL.cursor()

PATHS = {
    "favicon.ico" : f"{DIRECTORY}\\assets\\icons\\favicon.ico",
}

class App(CTk):

    def __init__(root, user: str) -> None:
        super().__init__(
            fg_color="#202020",
        )
        root.user = user

        root.geometry("800x600")
        root.minsize(800, 600)
        root.maxsize(1000, 750)

        root.title("Echxus")
        root.iconbitmap(PATHS["favicon.ico"])

        change_border_color(root, "#202020")
        change_header_color(root, "#202020")

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        root.screen = Screen(root)
        root.screen.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        root.mainloop()

class Screen(CTkFrame):

    def __init__(screen, master: App) -> None:
        super().__init__(
            master,
            fg_color="#2c2c2c",
            corner_radius=20
        )
        screen.parent = master

        screen.columnconfigure(0, weight=75, uniform="a")
        screen.columnconfigure(1, weight=1, uniform="a")
        screen.columnconfigure(2, weight=178, uniform="a")
        screen.rowconfigure(0, weight=1)

        screen.divider = CTkLabel(screen, bg_color="#202020", text="")
        screen.divider.grid(column=1, row=0, sticky="nsew")

        screen.navigation = Navigation(screen)
        screen.navigation.grid(column=0, row=0, sticky="nsew")

        screen.chat = Chat(screen)
        screen.chat.grid(column=2, row=0, sticky="nsew")

        set_opacity(screen.navigation, color="black")
        set_opacity(screen.chat, color="black")

class Navigation(CTkFrame):

    def __init__(nav, master: Screen) -> None:
        super().__init__(
            master,
            fg_color="#2c2c2c",
            corner_radius=20,
            bg_color="black"
        )
        nav.parent = master

        nav.label = CTkLabel(
            nav,
            text="Chats",
            fg_color="transparent",
            text_color="#ffffff",
            font=("JetBrains Mono Bold", 25)
        )
        nav.label.place(relx=0.25, rely=0.04, anchor="center")

        nav.contacts = Contacts(nav)
        nav.contacts.place(relx=0.5, rely=0.575, anchor="center", relheight=0.8, relwidth=0.9)

        nav.newChat = CTkButton(
            nav,
            text="📝",
            width=5,
            height=5,
            fg_color="#2c2c2c",
            hover_color="#3a3a3a",
            font=("JetBrains Mono Bold", 20),
            command=nav.contacts.append
        )
        nav.newChat.place(relx=0.87, rely=0.04, anchor="center")

        nav.searchVar = StringVar()
        nav.searchVar.trace_add("write", lambda *args: nav.update_contact_list())
        nav.searchBar = CTkEntry(
            nav,
            fg_color="#2c2c2c",
            border_color="#3a3a3a",
            font=("JetBrains Mono Bold", 20),
            textvariable=nav.searchVar
        )
        nav.searchBar.place(relx=0.5, rely=0.11, anchor="center", relwidth=0.9)

    def update_contact_list(nav):
        search_query = nav.searchVar.get().lower()
        for widget in nav.contacts.winfo_children():
            widget.destroy()
        nav.contacts.loaded.clear()
        for user in nav.contacts.friends:
            if search_query in user.lower():
                button = CTkButton(
                    nav.contacts,
                    fg_color="#373737",
                    text=user,
                    hover_color="#808080",
                    font=("JetBrains Mono Medium", 20)
                )
                nav.contacts.loaded[user] = button
                button.pack(pady=5, fill="x", padx=2)

class Contacts(CTkScrollableFrame):

    def __init__(frame, master: Navigation) -> None:
        super().__init__(
            master,
            fg_color="#3a3a3a",
        )
        frame.parent = master

        frame.loaded = {}
        frame.friends = literal_eval(SQL_CURSOR.execute("SELECT * FROM Info WHERE username = ?", (username,)).fetchone()[1])

        frame.load()

    def append(frame) -> None:
        frame.asker = askUser.Ask(username)
        try: frame.wait_window(frame.asker)
        except: return
        user = str(frame.asker)
        if not user: return

        frame.friends.append(user)
        frame.loaded[user] = CTkButton(
            frame,
            fg_color="#373737",
            text=user,
            hover_color="#808080",
            font=("JetBrains Mono Medium", 20)
        )
        frame.loaded[user].pack(pady=5, fill="x", padx=2)

        SQL_CURSOR.execute("UPDATE Info SET friends=? WHERE username=?", (str(frame.friends), username))
        SQL.commit()

    def load(frame) -> None:
        for user in frame.friends:
            frame.loaded[user] = CTkButton(
                frame,
                fg_color="#373737",
                text=user,
                hover_color="#808080",
                font=("JetBrains Mono Medium", 20)
            )
            frame.loaded[user].pack(pady=5, fill="x", padx=2)

class Chat(CTkFrame):

    def __init__(chat, master: Screen) -> None:
        super().__init__(
            master,
            fg_color="#2c2c2c",
            corner_radius=20,
            bg_color="black"
        )
        chat.parent = master

app = App(username)
SQL.close()