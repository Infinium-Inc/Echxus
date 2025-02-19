from source import login
if not login.username: exit()
username = login.username

from secrypto import decrypt, Key
from datetime import datetime
from customtkinter import *
from pywinstyles import *
from ast import literal_eval
from threading import Thread

from source import askUser, messaging, sync
from source.GLOBAL import SQL_CURSOR, GLOBAL_SQL, PATHS, GLOBAL_KEY

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
            command=nav.contacts.append,
            text_color="#ffffff"
        )
        nav.newChat.place(relx=0.87, rely=0.04, anchor="center")

        nav.searchVar = StringVar()
        nav.searchVar.trace_add("write", lambda *args: nav.update_contact_list())
        nav.searchBar = CTkEntry(
            nav,
            fg_color="#2c2c2c",
            border_color="#3a3a3a",
            font=("JetBrains Mono Bold", 20),
            textvariable=nav.searchVar,
            text_color="#ffffff"
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
                    font=("JetBrains Mono Medium", 20),
                    text_color="#ffffff"
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
            command=lambda user=user: frame.parent.parent.chat.open(user),
            text_color="#ffffff"
        )
        frame.loaded[user].pack(pady=5, fill="x", padx=2)

        SQL_CURSOR.execute("UPDATE Info SET friends=? WHERE username=?", (str(frame.friends), username))
        GLOBAL_SQL.commit()

    def load(frame) -> None:
        for user in frame.friends:
            frame.loaded[user] = CTkButton(
                frame,
                fg_color="#373737",
                text=user,
                hover_color="#808080",
                font=("JetBrains Mono Medium", 20),
                command=lambda user=user: frame.parent.parent.chat.open(user),
                text_color="#ffffff"
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
        chat.password = decrypt(SQL_CURSOR.execute("SELECT * FROM Users WHERE username=?", (username, )).fetchone()[2], GLOBAL_KEY)
        chat.chats = {}

        chat.header = CTkLabel(
            chat,
            text="No chat selected",
            font=("JetBrains Mono Bold", 20),
            text_color="#ffffff"
        )
        chat.header.pack(pady=10)

    def open(chat, chatName: str) -> None:
        for chat_ in chat.chats.values():
            chat_.pack_forget()

        if chatName not in chat.chats:
            chat.chats[chatName] = Opened(chat, chatName)

        chat.chats[chatName].pack(expand=True, fill="both")
        chat.header.configure(text=chatName)

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
        opened.columnconfigure(0, weight=8, uniform="a")
        opened.columnconfigure(1, weight=1, uniform="a")

        opened.loading = Loading(opened)

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
            text="📤",
            font=("", 20),
            hover_color="#1e1e1e",
            fg_color="#252526",
            border_color="#565b5e",
            border_width=2,
            command=opened.message,
            state="disabled",
            text_color="#ffffff"
        )
        opened.startButton.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    def writing(opened, *_) -> None:
        opened.startButton.configure(state="normal" if opened.entryVar.get() else "disabled")

    def message(opened, *_) -> None:
        opened.messages.message(opened.entryVar.get())
        opened.entryVar.set("")

class Loading(CTkLabel):

    def __init__(loading, master: Opened):
        super().__init__(
            master,
            text="Loading...",
            font=("JetBrains Mono Bold", 20),
            fg_color="#252526",
            text_color="#ffffff"
        )

    def load(loading):
        loading.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)
        loading.lift()

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
        messages.seed = Key(seed=int(SQL_CURSOR.execute("SELECT * FROM Users WHERE username = ?", (username, )).fetchone()[3]))

        messages.load()

        messages.sync = Thread(target=lambda: sync.check_for_new_messages(username, messages.friend, messages.add), daemon=True)
        messages.sync.start()

    def message(messages, string: str) -> None:
        messaging.send(username, string, messages.friend, messages.parent.parent.password)
        Message(
            messages,
            f"{datetime.now().date()} {datetime.now().hour}:{datetime.now().minute}.{datetime.now().second}",
            string,
            "e"
        ).pack(fill="x", padx=10, pady=5)

    def add(messages, message):
        Message(
            messages,
            message[0],
            decrypt(message[2], messages.seed),
            "w"
        ).pack(fill="x", padx=10, pady=5)

    def load(messages):
        messages.parent.loading.load()
        messages.update_idletasks()

        loaded = set()

        def load_messages():
            for time, sender, message in messaging.get_messages(username+"-"+messages.friend, messages.parent.parent.password):
                if time not in loaded:
                    Message(
                            messages,
                            time,
                            message,
                            "e" if username==sender else "w"
                        ).pack(fill="x", padx=10, pady=10)
                    loaded.add(time)

            messages.parent.after(0, messages.parent.loading.destroy)

        Thread(target=load_messages, daemon=True).start()

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
            anchor="w" if align == "w" else "e",
            text_color="#ffffff"
        )
        message.timeLabel.pack(fill="x", padx=10)

        message.textLabel = CTkTextbox(
            message,
            font=("JetBrains Mono Medium", 12 if len(text) > 250 else 16),
            wrap="none" if len(text) > 250 else "word",
            height=130 if len(text) > 250 else 40,
            state="normal",
            width=400 if len(text) > 250 else 250,
            text_color="#ffffff",
            fg_color="#1d1e1e"
        )
        message.textLabel.insert("1.0", text)
        message.textLabel.configure(state="disabled")
        message.textLabel.pack(padx=10, pady=5, anchor=align)

app = App(username)

GLOBAL_SQL.close()