from source import login, messaging, askUser
if not login.username: exit()
username = login.username

from secrypto import decrypt
from datetime import datetime
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
            font=("JetBrains Mono Medium", 20),
            command=lambda user=user: frame.parent.parent.chat.open(user)
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
                font=("JetBrains Mono Medium", 20),
                command=lambda user=user: frame.parent.parent.chat.open(user)
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
        chat.password = decrypt(SQL_CURSOR.execute("SELECT * FROM Users WHERE username=?", (username, )).fetchone()[2], login.GLOBAL_KEY)
        chat.chats = {}

    def open(chat, chatName: str) -> None:
        for chat_ in chat.chats.values():
            chat_.pack_forget()

        if chatName not in chat.chats:
            chat.chats[chatName] = Opened(chat, chatName)

        chat.chats[chatName].pack(expand=True, fill="both")

class Opened(CTkFrame):

    def __init__(opened, master: Chat, friend: str) -> None:
        super().__init__(
            master,
            fg_color="#252526",
            bg_color="#252525",
            corner_radius=25
        )
        opened.parent = master
        opened.friend = friend

        opened.rowconfigure(0, weight=7, uniform="a")
        opened.rowconfigure(1, weight=1, uniform="a")
        opened.columnconfigure(0, weight=9, uniform="a")
        opened.columnconfigure(1, weight=1, uniform="a")

        opened.messages = Messages(opened, friend)
        opened.messages.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)

        opened.entryVar = StringVar()
        opened.entryVar.trace("w", opened.writing)
        opened.entry = CTkEntry(
            opened,
            font=("JetBrains Mono Medium", 20),
            text_color="#cccccc",
            fg_color="#323233",
            corner_radius=10,
            textvariable=opened.entryVar
        )
        opened.entry.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        opened.startButton = CTkButton(
            opened,
            text="🏹",
            font=("", 20),
            hover_color="#1e1e1e",
            fg_color="#252526",
            border_color="#565b5e",
            border_width=2,
            command=opened.message,
            state="disabled"
        )
        opened.startButton.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    def writing(opened, *_) -> None:
        opened.startButton.configure(state="normal" if opened.entryVar.get() else "disabled")

    def message(opened) -> None:
        opened.messages.message(opened.entryVar.get())
        opened.entryVar.set("")

class Messages(CTkScrollableFrame):

    def __init__(messages, master: Opened, friend: str) -> None:
        super().__init__(
            master,
            fg_color="#252526",
            corner_radius=10,
            border_color="#565b5e",
            border_width=2,
        )
        messages.parent = master
        messages.friend = friend

        messages.load()

    def message(messages, string: str) -> None:
        messaging.send(username, string, messages.friend, messages.parent.parent.password)
        Message(
            messages,
            f"{datetime.now().date()} {datetime.now().hour}:{datetime.now().minute}.{datetime.now().second}",
            string,
            "e"
        ).pack(fill="x", padx=10, pady=5)

    def load(messages):
        for time, sender, message in messaging.get_messages(username+"-"+messages.friend, messages.parent.parent.password):
            Message(
                messages,
                time,
                message,
                "e" if username==sender else "w"
            ).pack(fill="x", padx=10, pady=10)

class Message(CTkFrame):

    def __init__(message, master: Messages, time: str, text: str, align: str) -> None:
        super().__init__(
            master,
            fg_color="transparent"
        )

        message.timeLabel = CTkLabel(
            message,
            text=time,
            font=("JetBrains Mono Light", 10),
            anchor="w" if align == "w" else "e"
        )
        message.timeLabel.pack(fill="x", padx=10)

        if len(text) <= 294:
            message.textLabel = CTkLabel(
                message,
                text=text,
                font=("JetBrains Mono Medium", 18),
                anchor="w" if align=="w" else "e",
                wraplength=400,
                justify="left" if align=="w" else "right"
            )
            message.textLabel.pack(fill="x", padx=10)
        else:
            message.textLabel = CTkTextbox(
                message,
                font=("JetBrains Mono Medium", 14),
                wrap="word",
                height=100
            )
            message.textLabel.insert("1.0", text)
            message.textLabel.configure(state="disabled")
            message.textLabel.pack(fill="x", padx=10, pady=5)

app = App(username)
SQL.close()