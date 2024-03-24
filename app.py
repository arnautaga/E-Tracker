import sqlite3
import os
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga import Label, TextInput, Button, Box, SplitContainer


class ExpenseCalculatorWithLogin(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.name)
        self.username_entry = TextInput()
        self.password_entry = TextInput(placeholder='Password')
        self.login_button = Button('Login', on_press=self.login)
        self.register_button = Button('Register', on_press=self.register)

        login_box = Box(
            children=[
                Label('Username:'),
                self.username_entry,
                Label('Password:'),
                self.password_entry,
                self.login_button,
                self.register_button
            ],
            style=Pack(direction=ROW)
        )

        self.expense_description = TextInput()
        self.expense_amount = TextInput()
        self.expense_type = Box('Expense Type')
        self.add_expense_button = Button('Add Expense', on_press=self.add_expense)
        self.show_graph_button = Button('Show Graph', on_press=self.show_graph)
        self.expenses_text = TextInput(readonly=True)

        expense_box = Box(
            children=[
                Label('Expense Description:'),
                self.expense_description,
                Label('Expense Amount:'),
                self.expense_amount,
                self.expense_type,
                self.add_expense_button,
                self.show_graph_button,
                self.expenses_text
            ],
            style=Pack(direction=COLUMN)
        )

        self.split = SplitContainer()
        self.split.content = [login_box, expense_box]

        self.main_window.content = self.split
        self.main_window.show()

        self.initialize_database()
        self.update_expense_types()
        self.update_expenses()

    def initialize_database(self):
        if not os.path.exists("expense_tracker.db"):
            conn = sqlite3.connect("expense_tracker.db")
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    expense_type TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expense_types (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    type TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)

            conn.commit()
            conn.close()

    def login(self, widget):
        username = self.username_entry.value
        password = self.password_entry.value

        if not username or not password:
            self.main_window.info_dialog("Error", "Please enter a username and password.")
            return

        conn = sqlite3.connect("expense_tracker.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            self.user_id = user[0]  # Almacena el ID de usuario en el atributo user_id
            self.split.content = [self.split.content[1]]
            self.main_window.info_dialog("Login Successful", f"Welcome, {username}!")
        else:
            self.main_window.error_dialog("Error", "Incorrect username or password.")
    def register(self, widget):
        username = self.username_entry.value
        password = self.password_entry.value

        if not username or not password:
            self.main_window.info_dialog("Error", "Please enter a username and password.")
            return

        conn = sqlite3.connect("expense_tracker.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

        conn.close()

        self.main_window.info_dialog("Registration Successful", "User registered successfully.")

    def add_expense(self, widget):
        description = self.expense_description.value
        amount = self.expense_amount.value
        expense_type = self.expense_type.value

        if description and amount and expense_type:
            try:
                amount = float(amount)

                conn = sqlite3.connect("expense_tracker.db")
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO expenses (user_id, description, amount, expense_type) VALUES (?, ?, ?, ?)",
                    (self.user_id, description, amount, expense_type)
                )
                conn.commit()

                conn.close()

                self.main_window.info_dialog("Expense Added", "Expense added successfully.")

                self.update_expenses()

                self.expense_description.value = ''
                self.expense_amount.value = ''
            except ValueError:
                self.main_window.error_dialog("Error", "Please enter a valid amount.")

    def update_expense_types(self):
        self.expense_type.items = []

        conn = sqlite3.connect("expense_tracker.db")
        cursor = conn.cursor()

        cursor.execute("SELECT type FROM expense_types WHERE user_id=?", (self.user_id,))
        expense_types = [row[0] for row in cursor.fetchall()]

        conn.close()

        self.expense_type.items = expense_types

    def update_expenses(self):
        self.expenses_text.value = ''

        conn = sqlite3.connect("expense_tracker.db")
        cursor = conn.cursor()

        cursor.execute("SELECT description, amount, expense_type FROM expenses WHERE user_id=?", (self.user_id,))
        user_expenses = cursor.fetchall()

        conn.close()

        for description, amount, expense_type in user_expenses:
            self.expenses_text.value += f"{description} (${amount:.2f}) - {expense_type}\n"

    def show_graph(self, widget):
        self.main_window.info_dialog("Coming Soon", "This feature will be added soon!")

def main():
    return ExpenseCalculatorWithLogin('E-Tracker', app_id='com.example.etracker')

if __name__ == '__main__':
    app = main()
    app.main_loop()
