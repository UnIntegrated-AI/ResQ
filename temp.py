
import socket
import json
import csv
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QFrame, QLineEdit , QPushButton, QDialog, QVBoxLayout, QComboBox, QSpinBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QUrl


centre = Qt.AlignmentFlag.AlignCenter
top = Qt.AlignmentFlag.AlignTop
bottom = Qt.AlignmentFlag.AlignBottom
left = Qt.AlignmentFlag.AlignLeft
default = Qt.AlignmentFlag(0)

class App(QApplication):
    def __init__(self):
        super().__init__()

        self.window = QWidget()

        self.window.resize(800,500)
        self.window.setWindowTitle("ResQ")

        layout = QGridLayout(self.window)

        lf = loginframe(self.window, layout)

        layout.addWidget(lf, 0, 0)

        self.window.show()

class user_details(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.setStyleSheet("border: 1px solid orange; background-color: blue;")

        l = QLabel("userdetails")
        
        lud = QGridLayout(self)
        lud.addWidget(l)

class maincontainer(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        lmc = QGridLayout(self)

        udf = user_details(self)
        udf.setMaximumWidth(200)
        lmc.addWidget(udf,0,1)
        mff = mainframe(self)
        mff.setMaximumWidth(600)
        lmc.addWidget(mff,0,0)

class mainframe(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.lmf = QGridLayout(self)

        nav_container = QFrame(self)
        ncl = QGridLayout(nav_container)
        nav_container.setStyleSheet("QFrame{border: 1px solid orange;}")
        self.lmf.addWidget(nav_container,0,0, alignment=top)

        report_btn = QPushButton("Report an Accident", nav_container)
        report_btn.clicked.connect(self.report)
        ncl.addWidget(report_btn,0,0)

        yreports_btn = QPushButton("My Reports", nav_container)
        ncl.addWidget(yreports_btn,0,1)


        ncl.setAlignment(centre|left)
        self.lmf.setRowStretch(0,0)
        self.lmf.setRowStretch(1,1)
    
    def report(self):
        reportf = QFrame(self)
        reportf.setStyleSheet("QFrame{border: 1px solid orange;}")
        self.lmf.addWidget(reportf)
        rptfl = QGridLayout(reportf)

        rptfl.setRowStretch(0,1)
        rptfl.setRowStretch(1,1)
        rptfl.setRowStretch(2,1)
        rptfl.setRowStretch(3,1)

        styl = "margin: 30 100;"

        location_combo = QComboBox(reportf)
        reader = ["hello", "world"]
        for row in reader:
            if row:
                location_combo.addItem(row)
        result = location_combo.currentText()
        print(result)
        rptfl.addWidget(location_combo, 0,0, alignment=centre | default)

        
        
        npa = QSpinBox(reportf)
        npa.setMinimum(1)
        npa.setMaximum(100)
        rptfl.addWidget(npa, 1,0)


        type_of_accidents = ["Road Accident", "Landslide", "Fuel", "Motor support"]

        taccd = QComboBox(reportf)
        for a in type_of_accidents:
            taccd.addItem(a)
        rptfl.addWidget(taccd, 2,0)

    def open_map(self):

        self.map_window = QDialog(self)

        self.map_window.setWindowTitle("Select Location")
        self.map_window.resize(900, 600)

        layout = QVBoxLayout(self.map_window)

        self.map_view = QWebEngineView()

        self.map_view.setUrl(
            QUrl.fromLocalFile(
                "map.html"
            )
        )

        layout.addWidget(self.map_view)

        self.map_view.setUrl(self.map_url)

        layout.addWidget(self.map_view)

        self.map_window.show()

class loginframe(QFrame):
    def __init__(self, parent, layoutapp):
        super().__init__(parent)

        self.parent = parent
        self.layoutapp = layoutapp

        self.setStyleSheet("""
            QFrame {
                background-color: #F4F7FA;
            }

            QLabel#title {
                color: #172033;
                font-size: 32px;
                font-weight: bold;
            }

            QLabel#subtitle {
                color: #6B7280;
                font-size: 14px;
            }

            QLineEdit {
                background-color: white;
                color: #172033;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 2px solid #DC2626;
            }

            QPushButton {
                background-color: #DC2626;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 11px;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #B91C1C;
            }

            QPushButton:pressed {
                background-color: #991B1B;
            }
        """)

        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setVerticalSpacing(12)

        # Title
        title = QLabel("ResQ")
        title.setObjectName("title")
        title.setAlignment(centre)

        # Subtitle
        subtitle = QLabel("Emergency Response & Reporting")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(centre)

        # Username
        self.uentry = QLineEdit()
        self.uentry.setPlaceholderText("Username")
        self.uentry.setFixedSize(350, 45)

        # Password
        self.pentry = QLineEdit()
        self.pentry.setPlaceholderText("Password")
        self.pentry.setEchoMode(QLineEdit.EchoMode.Password)
        self.pentry.setFixedSize(350, 45)

        # Login button
        btn = QPushButton("LOGIN")
        btn.setFixedSize(350, 45)
        btn.clicked.connect(self.login_btn)

        # Layout
        layout.addWidget(title, 0, 0)
        layout.addWidget(subtitle, 1, 0)
        layout.setSpacing(15)
        layout.addWidget(self.uentry, 3, 0)
        layout.addWidget(self.pentry, 4, 0)
        layout.setSpacing(10)
        layout.addWidget(btn, 6, 0)

    def login_btn(self):
        uname = self.uentry.text().strip()
        passwd = self.pentry.text()

        if True:
            print("Enter username and password.")
            # return

            print(f"username: {uname}")
            print(f"password: {passwd}")

            self.uentry.clear()
            self.pentry.clear()

            self.hide()

            mc = maincontainer(self.parent)
            self.layoutapp.addWidget(mc, 0, 0)

#hello

app = App()
app.exec()



# End Line