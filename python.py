import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QDialog, QFormLayout, QMessageBox
)

class AuthManager:
    def __init__(self, users_file="users.json"):
        self.users_file = users_file
        self.load_users()

    def load_users(self):
        try:
            with open(self.users_file, 'r') as file:
                self.users = json.load(file)
        except FileNotFoundError:
            self.users = []

    def save_users(self):
        with open(self.users_file, 'w') as file:
            json.dump(self.users, file, indent=4)

    def register_user(self, username, password):
        self.users.append({'username': username, 'password': password})
        self.save_users()

    def check_credentials(self, username, password):
        for user in self.users:
            if user['username'] == username and user['password'] == password:
                return True
        return False

class ObjectManager:
    def __init__(self, objects_file="objects.json"):
        self.objects_file = objects_file
        self.load_objects()

    def load_objects(self):
        try:
            with open(self.objects_file, 'r') as file:
                self.objects = json.load(file)
        except FileNotFoundError:
            self.objects = []

    def save_objects(self):
        with open(self.objects_file, 'w') as file:
            json.dump(self.objects, file, indent=4)

    def add_object(self, obj):
        self.objects.append(obj)
        self.save_objects()

    def update_object(self, index, obj):
        self.objects[index] = obj
        self.save_objects()

    def remove_object(self, index):
        del self.objects[index]
        self.save_objects()

class LoginForm(QDialog):
    def __init__(self, auth_manager):
        super().__init__()

        self.auth_manager = auth_manager
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)

        login_button = QPushButton("Login")
        register_button = QPushButton("Register")

        login_button.clicked.connect(self.login)
        register_button.clicked.connect(self.register)

        layout.addRow(login_button, register_button)

        self.setLayout(layout)
        self.setWindowTitle("Login")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if self.auth_manager.check_credentials(username, password):
            self.accept()
        else:
            QMessageBox.warning(self, "Thông báo", "Tên người dùng hoặc mật khẩu không đúng !")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username and password:
            self.auth_manager.register_user(username, password)
            QMessageBox.information(self, "Thông báo", "Người dùng đã đăng ký thành công.")
        else:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập cả tên người dùng và mật khẩu.")

class ObjectManagerApp(QWidget):
    def __init__(self, auth_manager, object_manager):
        super().__init__()

        self.auth_manager = auth_manager
        self.object_manager = object_manager

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Object Manager")
        self.setGeometry(100, 100, 600, 400)

        self.main_layout = QVBoxLayout()

        self.object_list_widget = QListWidget()

        self.add_button = QPushButton("Add")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.logout_button = QPushButton("Logout")
        self.search_input = QLineEdit()
        self.search_button = QPushButton("Search")

        self.add_button.clicked.connect(self.show_add_dialog)
        self.edit_button.clicked.connect(self.show_edit_dialog)
        self.delete_button.clicked.connect(self.delete_object)
        self.logout_button.clicked.connect(self.logout)
        self.search_button.clicked.connect(self.search_objects)

        self.main_layout.addWidget(QLabel("Object List:"))
        self.main_layout.addWidget(self.object_list_widget)
        self.main_layout.addWidget(self.add_button)
        self.main_layout.addWidget(self.edit_button)
        self.main_layout.addWidget(self.delete_button)
        self.main_layout.addWidget(self.logout_button)
        self.main_layout.addWidget(self.search_input)
        self.main_layout.addWidget(self.search_button)

        self.setLayout(self.main_layout)

        self.update_object_list()

    def show_add_dialog(self):
        add_dialog = ObjectDialog(self)
        if add_dialog.exec_() == QDialog.Accepted:
            obj = add_dialog.get_object()
            self.object_manager.add_object(obj)
            self.update_object_list()

    def show_edit_dialog(self):
        selected_item = self.object_list_widget.currentItem()
        if selected_item:
            index = self.object_list_widget.currentRow()
            edit_dialog = ObjectDialog(self, self.object_manager.objects[index])
            if edit_dialog.exec_() == QDialog.Accepted:
                obj = edit_dialog.get_object()
                self.object_manager.update_object(index, obj)
                self.update_object_list()

    def delete_object(self):
        selected_item = self.object_list_widget.currentItem()
        if selected_item:
            index = self.object_list_widget.currentRow()
            confirm_dialog = QMessageBox.question(self, "Thông báo", "Bạn có chắc chắn muốn xóa đối tượng này?",
                                                  QMessageBox.Yes | QMessageBox.No)
            if confirm_dialog == QMessageBox.Yes:
                self.object_manager.remove_object(index)
                self.update_object_list()

    def update_object_list(self):
        self.object_list_widget.clear()
        for obj in self.object_manager.objects:
            self.object_list_widget.addItem(obj['name'])

    def logout(self):
        self.close()

    def search_objects(self):
        search_term = self.search_input.text().lower()
        results = [obj for obj in self.object_manager.objects if
                   search_term in obj['name'].lower() or search_term in obj['info'].lower()]

        self.object_list_widget.clear()
        for obj in results:
            self.object_list_widget.addItem(obj['name'])

class ObjectDialog(QDialog):
    def __init__(self, parent, obj=None):
        super().__init__(parent)

        self.obj = obj if obj else {}

        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.info_input = QLineEdit()

        layout.addRow("Name:", self.name_input)
        layout.addRow("Info:", self.info_input)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)

        layout.addRow(save_button)

        if self.obj:
            self.name_input.setText(self.obj.get('name', ''))
            self.info_input.setText(self.obj.get('info', ''))

        self.setLayout(layout)
        self.setWindowTitle("Object Details")

    def get_object(self):
        return {'name': self.name_input.text(), 'info': self.info_input.text()}

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Auth Manager Setup
    auth_manager = AuthManager()

    # Object Manager Setup
    object_manager = ObjectManager()

    # Main Application
    login_form = LoginForm(auth_manager)
    if login_form.exec_() == QDialog.Accepted:
        main_app = ObjectManagerApp(auth_manager, object_manager)
        main_app.show()
        sys.exit(app.exec_())
