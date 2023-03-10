def gen():
    import sys
    import string
    import random
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QMessageBox, QLineEdit, QWidget
    from PyQt5.QtCore import Qt


    def random_string(length):
        letters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(letters) for i in range(length))

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Password Generator")
            self.setGeometry(100,100,400,200)
            

            # password length slider
            self.slider = QSlider(Qt.Horizontal)
            self.slider.setRange(8, 32)
            self.slider.setValue(8)
            self.slider.valueChanged.connect(self.slider_value_changed)

            # password length display
            self.length_label = QLabel("                                  Password Length: 8")

            # generate password button
            self.generate_button = QPushButton("Generate Password")
            self.generate_button.clicked.connect(self.generate_password)

            # clear password button
            self.clear_button = QPushButton("Clear Password")
            self.clear_button.clicked.connect(self.clear_password)

            # password display
            self.password_field = QLineEdit()
            self.password_field.setReadOnly(True)

            # copy password button
            self.copy_button = QPushButton("Copy Password")
            self.copy_button.clicked.connect(self.copy_password)

            # layout
            v_layout = QVBoxLayout()
            v_layout.addWidget(self.slider)
            v_layout.addWidget(self.length_label)
            v_layout.addWidget(self.generate_button)
            v_layout.addWidget(self.clear_button)
            v_layout.addWidget(self.password_field)
            v_layout.addWidget(self.copy_button)

            # create a central widget
            central_widget = QWidget()
            central_widget.setLayout(v_layout)

            # set the central widget
            self.setCentralWidget(central_widget)

        def slider_value_changed(self):
            value = self.slider.value()
            self.length_label.setText(f"                                  Password Length: {value}")

        def generate_password(self):
            length = self.slider.value()
            password = random_string(length)
            self.password_field.setText(password)
        
        def clear_password(self):
            if self.password_field.text() == "":
                message = QMessageBox()
                message.setWindowTitle("Failed")
                message.setText("There is nothing to clear.")
                message.exec_()
            else:
                self.password_field.setText("")

        def copy_password(self):
            if self.password_field.text() == "":
                message = QMessageBox()
                message.setWindowTitle("Failed.")
                message.setText("You must generate a password first.")
                message.exec_()
            else:
                self.password_field.selectAll()
                self.password_field.copy()

                message = QMessageBox()
                message.setWindowTitle("Succes")
                message.setText("Password copied to clipboard.")
                message.exec_()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

#gen()