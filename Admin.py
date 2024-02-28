import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit, QTableWidget, QTableWidgetItem
import psycopg2
import websockets

class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.login_label = QLabel("Логин:")
        self.login_input = QLineEdit(self)
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Войти", self)
        self.login_button.clicked.connect(self.login)

        self.layout.addWidget(self.login_label)
        self.layout.addWidget(self.login_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)

        self.central_widget.setLayout(self.layout)

        # Добавляем атрибут для хранения ссылки на окно DatabaseViewer
        self.database_viewer = None
        self.site_input_window = None  # Добавляем атрибут для окна SiteInputWindow

        # Настройка WebSocket
        self.websocket_server = "ws://localhost:8765"
        self.websocket = None

    def login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        # Подключаемся к серверу PostgreSQL
        connection = psycopg2.connect(
            user="postgres",
            password="1090",
            host="localhost",
            database="projects",
            port="5432",
            client_encoding="utf-8"
        )


        cur = connection.cursor()

        # Проверяем, существует ли пользователь в базе данных
        cur.execute("SELECT * FROM admins WHERE login = %s AND password = %s", (login, password))
        user = cur.fetchone()

        if user is None:
            self.show_message("Ошибка входа", "Неверный логин или пароль")
        else:
            # Создаем экземпляр DatabaseViewer
            if not self.database_viewer:
                self.database_viewer = DatabaseViewer(self.websocket_send)
                self.database_viewer.show()  # Показываем окно DatabaseViewer

            # Создаем экземпляр SiteInputWindow
            if not self.site_input_window:
                self.site_input_window = SiteInputWindow(self.websocket_send)
                self.site_input_window.show()  # Показываем окно SiteInputWindow

        cur.close()
        connection.close()

        # Подключаемся к WebSocket-серверу
        asyncio.ensure_future(self.connect_to_websocket())

    def show_message(self, title, text, QMessageBox):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.exec_()

    async def connect_to_websocket(self):
        async with websockets.connect(self.websocket_server) as websocket:
            self.websocket = websocket
            while True:
                message = await websocket.recv()
                print(f"Received message: {message}")

    def websocket_send(self, message):
        if self.websocket:
            asyncio.ensure_future(self.websocket.send(message))


class DatabaseViewer(QMainWindow):
    def __init__(self, websocket_send):
        super(DatabaseViewer, self)._init_()
        self.websocket_send = websocket_send

        self.setWindowTitle("Database Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.sql_label = QLabel("Enter SQL Query:")
        self.sql_input = QLineEdit(self)
        self.execute_button = QPushButton("Execute Query", self)
        self.execute_button.clicked.connect(self.execute_query)

        self.lisskins_button = QPushButton("Lisskins", self)
        self.lisskins_button.clicked.connect(self.show_lisskins_table)

        self.skinport_button = QPushButton("Skinport", self)
        self.skinport_button.clicked.connect(self.show_skinport_table)

        self.skinwallet_button = QPushButton("Skinwallet", self)
        self.skinwallet_button.clicked.connect(self.show_skinwallet_table)

        self.result_label = QLabel("Query Result:")
        self.table_widget = QTableWidget(self)

        self.layout.addWidget(self.sql_label)
        self.layout.addWidget(self.sql_input)
        self.layout.addWidget(self.execute_button)
        self.layout.addWidget(self.lisskins_button)
        self.layout.addWidget(self.skinport_button)
        self.layout.addWidget(self.skinwallet_button)
        self.layout.addWidget(self.result_label)
        self.layout.addWidget(self.table_widget)

        self.central_widget.setLayout(self.layout)

        self.current_table = None

    def execute_query(self):
        # Получаем SQL-запрос из QLineEdit
        sql_query = self.sql_input.text()
        self.websocket_send("База данных обновлена")
        self.websocket_send("База данных обновлена")

        try:
            connection = psycopg2.connect(
                user="postgres",
                password="1090",
                host="localhost",
                database="projects",
                port="5432"
            )

            cursor = connection.cursor()
            cursor.execute(sql_query)

            # Получаем имена столбцов
            columns = [desc[0] for desc in cursor.description]

            # Устанавливаем заголовки столбцов в виджете таблицы
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)

            # Заполняем таблицу данными
            self.table_widget.setRowCount(0)
            for row in cursor.fetchall():
                row_position = self.table_widget.rowCount()
                self.table_widget.insertRow(row_position)
                for col_index, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table_widget.setItem(row_position, col_index, item)

            connection.close()

            self.current_table = None

        except psycopg2.Error as e:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            self.table_widget.setHorizontalHeaderLabels([])
            self.table_widget.setPlainText(f"Error executing query: {e}")

    def show_lisskins_table(self):
        if self.current_table != "lisskins":
            sql_query = "SELECT * FROM lisskins"
            self.sql_input.setText(sql_query)
            self.execute_query()
            self.current_table = "lisskins"

    def show_skinport_table(self):
        if self.current_table != "skinport":
            sql_query = "SELECT * FROM skinport"
            self.sql_input.setText(sql_query)
            self.execute_query()
            self.current_table = "skinport"

    def show_skinwallet_table(self):
        if self.current_table != "skinwallet":
            sql_query = "SELECT * FROM skinwallet"
            self.sql_input.setText(sql_query)
            self.execute_query()
            self.current_table = "skinwallet"

class SiteInputWindow(QMainWindow):
    def __init__(self, websocket_send):
        super(SiteInputWindow, self)._init_()
        self.websocket_send = websocket_send

        self.setWindowTitle("Site Input")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.name_label = QLabel("Имя сайта которые вы хотели бы добавить:")
        self.name_input = QLineEdit(self)
        self.link_label = QLabel("Ссылка на сайт:")
        self.link_input = QLineEdit(self)
        self.save_button = QPushButton("Save Data", self)
        self.save_button.clicked.connect(self.save_data)

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.link_label)
        self.layout.addWidget(self.link_input)
        self.layout.addWidget(self.save_button)

        self.central_widget.setLayout(self.layout)


    def save_data(self):
        name = self.name_input.text()
        link = self.link_input.text()
        # Остальной код save_data
        # После сохранения данных отправляем сообщение в WebSocket
        self.websocket_send("Данные сохранены")
        try:
            connection = psycopg2.connect(
                user="postgres",
                password="1090",
                host="localhost",
                database="projects",
                port="5432"
            )

            cursor = connection.cursor()
            query = "INSERT INTO sait (name, link) VALUES (%s, %s);"
            cursor.execute(query, (name, link))
            connection.commit()
            connection.close()

            self.show_message("Success", "Data saved successfully.")
        except psycopg2.Error as e:
            print("Error connecting to the database:", e)

    def show_message(self, title, text, QPlainTextEdit):
        msg_box = QPlainTextEdit()
        msg_box.setPlainText(f"{title}\n{text}")

        # Устанавливаем стиль
        msg_box.setStyleSheet(
            "QPlainTextEdit { background-color: #E6E6FA; font-size: 18px; }"
        )

        # Создаем вертикальный layout и добавляем в него виджет
        layout = QVBoxLayout()
        layout.addWidget(msg_box)

        # Создаем окно
        message_window = QWidget()
        message_window.setLayout(layout)

        message_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec_())