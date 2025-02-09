from customtkinter import *
from pywinstyles import *
from re import sub, match, search
from os import path, makedirs
from sqlite3 import  Connection
from secrypto import Key, encrypt, decrypt

DIRECTORY = f"C:\\Users\\Public\\AppData\\Echxus"
if not path.exists(DIRECTORY):
    makedirs(DIRECTORY)

GLOBAL_KEY = Key(seed=4852572164214751712476216756)

SQL = Connection(DIRECTORY+"\\database.db")
SQL_CURSOR = SQL.cursor()
SQL_CURSOR.execute("CREATE TABLE IF NOT EXISTS Users (username TEXT, name TEXT, password TEXT, seed TEXT)")
SQL.create_function("decrypt", 1, lambda x: decrypt(x, GLOBAL_KEY))
SQL.create_function("encrypt", 1, lambda x: encrypt(x, GLOBAL_KEY))

PATHS = {
    "favicon.ico" : f"{DIRECTORY}\\assets\\icons\\favicon.ico",
}

class App(CTk):

    def __init__(root):
        super().__init__(fg_color="#2c2c2c")
        root.user = None

        root.title("Echxus | Login")
        root.iconbitmap(PATHS["favicon.ico"])
        root.geometry("600x400")
        root.resizable(False, False)

        change_border_color(root, "#2c2c2c")
        change_header_color(root, "#2c2c2c")

        root.authPage = AuthPage(root)
        root.authPage.pack(fill="both", expand=True, padx=20, pady=20)

        root.mainloop()

class AuthPage(CTkTabview):

    def __init__(page, master: App):
        super().__init__(
            master,
            fg_color="#202020",
            segmented_button_fg_color="#202020",
            segmented_button_selected_color="#333333",
            segmented_button_selected_hover_color="#333333",
            segmented_button_unselected_hover_color="#202020",
            segmented_button_unselected_color="#202020",
            text_color="#878787",
        )

        page.add("Register")
        page.add("Login")

        page.registerPage = RegisterPage(page.tab("Register"), page)
        page.registerPage.pack(fill="both", expand=True)

        page.loginPage = LoginPage(page.tab("Login"), page)
        page.loginPage.pack(fill="both", expand=True)

    def finish(page, user):
        page.master.user = user
        page.master.destroy()

class RegisterPage(CTkFrame):

    def __init__(page, master, parent):
        super().__init__(
            master,
            fg_color="#202020",
            corner_radius=15
        )
        page.master = master
        page.parent = parent

        page.rowconfigure(0, weight=1, uniform="a")
        page.rowconfigure((1, 2, 3, 4), weight=3, uniform="a")
        page.rowconfigure(5, weight=1, uniform="a")
        page.columnconfigure(0, weight=1, uniform="a")

        page.usernameVar = StringVar()
        page.usernameVar.trace("w", page.usernameCorrect)
        page.usernameVar.trace("w", page.usernameVerify)
        page.username = CTkEntry(
            page,
            fg_color="#202020",
            font=("JetBrains Mono Light", 20),
            textvariable=page.usernameVar
        )
        page.username.grid(row=1, column=0, sticky="nsew", padx=50, pady=15)

        page.usernameTitle = CTkLabel(
            page,
            text="Username ",
            fg_color="#202020",
            font=("JetBrains Mono Light", 12)
        )
        set_opacity(page.usernameTitle, color="#202020")
        page.usernameTitle.grid(row=1, column=0, sticky="nw", padx=47)

        page.usernameAvailableVar = StringVar(value="username unavailable")
        page.usernameAvailable = CTkLabel(
            page,
            textvariable=page.usernameAvailableVar,
            fg_color="#202020",
            font=("JetBrains Mono Light", 10),
            text_color="#ff5370"
        )
        set_opacity(page.usernameAvailable, color="#202020")
        page.usernameAvailable.grid(row=1, column=0, sticky="sw", padx=47, pady=3)

        page.passwordVar = StringVar()
        page.passwordVar.trace("w", page.passwordVerify)
        page.password = CTkEntry(
            page,
            fg_color="#202020",
            font=("JetBrains Mono Light", 20),
            textvariable=page.passwordVar,
            show="•"
        )
        page.password.grid(row=2, column=0, sticky="nsew", padx=50, pady=15)

        page.passwordTitle = CTkLabel(
            page,
            text="Password ",
            fg_color="#202020",
            font=("JetBrains Mono Light", 12)
        )
        set_opacity(page.passwordTitle, color="#202020")
        page.passwordTitle.grid(row=2, column=0, sticky="nw", padx=47)

        page.passwordRequirementsVar = StringVar(value="password must be atleast 5 characters long")
        page.passwordRequirements = CTkLabel(
            page,
            textvariable=page.passwordRequirementsVar,
            fg_color="#202020",
            font=("JetBrains Mono Light", 10),
            text_color="#ff5370"
        )
        set_opacity(page.passwordRequirements, color="#202020")
        page.passwordRequirements.grid(row=2, column=0, sticky="sw", padx=47, pady=3)

        page.passwordToggle = CTkLabel(
            page,
            text="🔒",
            fg_color="#202020",
            font=("JetBrains Mono Light", 15),
            cursor="hand2"
        )
        page.passwordToggle.grid(row=2, column=0, sticky="e", padx=55)
        page.passwordToggle.bind("<Button-1>", page.passwordToggleClick)

        page.nameVar = StringVar()
        page.nameVar.trace("w", page.nameCorrect)
        page.name = CTkEntry(
            page,
            fg_color="#202020",
            font=("JetBrains Mono Light", 20),
            textvariable=page.nameVar,
        )
        page.name.grid(row=3, column=0, sticky="nsew", padx=50, pady=15)

        page.nameTitle = CTkLabel(
            page,
            text="Name (optional) ",
            fg_color="#202020",
            font=("JetBrains Mono Light", 12)
        )
        set_opacity(page.nameTitle, color="#202020")
        page.nameTitle.grid(row=3, column=0, sticky="nw", padx=47)

        page.submit = CTkButton(
            page,
            text="REGISTER",
            fg_color="#202020",
            hover_color="#333333",
            font=("JetBrains Mono Bold", 25),
            command=page.submitClick
        )
        page.submit.grid(row=4, column=0)

    def usernameCorrect(page, *_):
        text = page.usernameVar.get()

        if text != "":
            if len(text) > 35: page.usernameVar.set(text[:35])
            elif " " in text: page.usernameVar.set(text.replace(" ", "_"))
            elif not match(r"^[\w\d_]*$", text): page.usernameVar.set(sub(r'[^a-zA-Z0-9_]', '', text))
            elif text[0] in "1234567890": page.usernameVar.set(text[1:])

    def usernameVerify(page, *_):
        usernames = SQL_CURSOR.execute("SELECT username FROM Users").fetchall()
        usernames = [i[0] for i in usernames]

        username = page.usernameVar.get()

        if len(username) >= 5:
            if username in usernames:
                page.usernameAvailableVar.set("username unavailable")
                page.usernameAvailable.configure(text_color="#ff5370")
            else:
                page.usernameAvailableVar.set("username available")
                page.usernameAvailable.configure(text_color="#64ffda")
        else:
            page.usernameAvailableVar.set("username unavailable")
            page.usernameAvailable.configure(text_color="#ff5370")

    def nameCorrect(page, *_):
        text = page.nameVar.get()

        if text != "":
            if len(text) > 35: page.nameVar.set(text[:35])
            elif not match(r'^[a-zA-Z\s]+$', text): page.nameVar.set(sub(r'[^a-zA-Z\s]', '', text))

    def passwordToggleClick(page, *_):
        if page.password.cget("show") == "•":
            page.password.configure(show="")
            page.passwordToggle.configure(text="🔓")
        else:
            page.password.configure(show="•")
            page.passwordToggle.configure(text="🔒")

    def passwordVerify(page, *_):
        text = page.passwordVar.get()

        if text != "":
            good = False
            if len(text) < 5: page.passwordRequirementsVar.set("password must be atleast 5 characters long")
            elif not search(r"\d", text): page.passwordRequirementsVar.set("password must contain a number")
            elif text.isnumeric(): page.passwordRequirementsVar.set("password must contain a letter")
            elif len(text) > 25: page.passwordRequirementsVar.set("password can not be more than 25 characters")
            else:
                good = True
                page.passwordRequirementsVar.set("password is okay")
            if good: page.passwordRequirements.configure(text_color="#64ffda")
            else: page.passwordRequirements.configure(text_color="#ff5370")
        else:
            page.passwordRequirementsVar.set("password must be atleast 5 characters long")

    def submitClick(page):
        username = page.usernameVar.get()
        password = page.passwordVar.get()
        name = page.nameVar.get()

        if page.passwordRequirementsVar.get() != "password is okay": return
        if page.usernameAvailableVar.get() != "username available": return
        if name == "": name = username

        unique = Key()

        SQL_CURSOR.execute("INSERT INTO Users (username, name, password, seed) VALUES (?, ENCRYPT(?), ENCRYPT(?), ENCRYPT(?))", (username, name, password, str(unique.seed)))
        SQL.commit()

        page.parent.finish(username)

class LoginPage(CTkFrame):

    def __init__(page, master, parent):
        super().__init__(
            master,
            fg_color="#202020",
            corner_radius=15
        )
        page.master = master
        page.parent = parent

        page.rowconfigure(0, weight=1, uniform="a")
        page.rowconfigure((1, 2, 3, 4), weight=3, uniform="a")
        page.rowconfigure(5, weight=1, uniform="a")
        page.columnconfigure(0, weight=1, uniform="a")

        page.usernameVar = StringVar()
        # page.usernameVar.trace("w", page.usernameCorrect)
        page.username = CTkEntry(
            page,
            fg_color="#202020",
            font=("JetBrains Mono Light", 20),
            textvariable=page.usernameVar
        )
        page.username.grid(row=1, column=0, sticky="nsew", padx=50, pady=15)

        page.usernameTitle = CTkLabel(
            page,
            text="Username ",
            fg_color="#202020",
            font=("JetBrains Mono Light", 12)
        )
        set_opacity(page.usernameTitle, color="#202020")
        page.usernameTitle.grid(row=1, column=0, sticky="nw", padx=47)

        page.passwordVar = StringVar()
        page.password = CTkEntry(
            page,
            fg_color="#202020",
            font=("JetBrains Mono Light", 20),
            textvariable=page.passwordVar,
            show="•"
        )
        page.password.grid(row=2, column=0, sticky="nsew", padx=50, pady=15)

        page.passwordTitle = CTkLabel(
            page,
            text="Password ",
            fg_color="#202020",
            font=("JetBrains Mono Light", 12)
        )
        set_opacity(page.passwordTitle, color="#202020")
        page.passwordTitle.grid(row=2, column=0, sticky="nw", padx=47)

        page.passwordToggle = CTkLabel(
            page,
            text="🔒",
            fg_color="#202020",
            font=("JetBrains Mono Light", 15),
            cursor="hand2"
        )
        page.passwordToggle.grid(row=2, column=0, sticky="e", padx=55)
        page.passwordToggle.bind("<Button-1>", page.passwordToggleClick)

        page.submit = CTkButton(
            page,
            text="LOGIN",
            fg_color="#202020",
            hover_color="#333333",
            font=("JetBrains Mono Bold", 25),
            command=page.submitClick
        )
        page.submit.grid(row=4, column=0)

    def passwordToggleClick(page, *_):
        if page.password.cget("show") == "•":
            page.password.configure(show="")
            page.passwordToggle.configure(text="🔓")
        else:
            page.password.configure(show="•")
            page.passwordToggle.configure(text="🔒")

    def submitClick(page):
        username = page.usernameVar.get()
        password = page.passwordVar.get()

        user = SQL_CURSOR.execute("SELECT * FROM Users WHERE username = ? AND DECRYPT(password) = ?", (username, password)).fetchone()

        if user: page.parent.finish(username)
        else: page.notify()

    def notify(page):
        page.notification = CTkLabel(
            page,
            text="Invalid username or password",
            fg_color="#202020",
            font=("JetBrains Mono Medium", 20),
            text_color="#ff5370"
        )
        page.notification.grid(row=3, column=0, sticky="nsew", padx=50, pady=15)

app = App()
SQL.close()

username = app.user