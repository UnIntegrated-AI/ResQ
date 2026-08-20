import socket
import json
import csv
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QFrame, QLineEdit , QPushButton, QDialog, QVBoxLayout, QComboBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QUrl

import geopandas as gpd
import folium
# import matplotlib.pylot as plt
import matplotlib

white ="#F4F7FA"

centre = Qt.AlignmentFlag.AlignCenter
top = Qt.AlignmentFlag.AlignTop
bottom = Qt.AlignmentFlag.AlignBottom
left = Qt.AlignmentFlag.AlignLeft

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


class loginframe(QFrame):
    def __init__(self, parent, layoutapp):
        super().__init__(parent)
        self.parent = parent
        self.layoutapp = layoutapp
        lm = QGridLayout(self)

        self.setStyleSheet("""
                    QFrame {
                        background-color: #F4F7FA;
                    }
        
                    QLabel#title {
                        color: #DC2626;
                        font-size: 32px;
                        font-weight: bold;
                    }
        
                    QLabel#subtitle {
                        color: #6B7280;
                        font-size: 20px;
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

        lm.setVerticalSpacing(0)

        title = QLabel("ResQ")
        title.setObjectName("title")
        lm.addWidget(title, 0, 0, alignment=centre | bottom)

        subtitle = QLabel("Login")
        subtitle.setObjectName("subtitle")
        lm.addWidget(subtitle, 1, 0, alignment=centre |bottom)

        self.uentry = QLineEdit(self)
        self.uentry.setPlaceholderText("Username")
        self.uentry.setMinimumSize(400,30)
        # self.uentry.setStyleSheet(style)
        lm.addWidget(self.uentry, 2,0, alignment=centre)

        self.pentry = QLineEdit(self)
        self.pentry.setPlaceholderText("Password")
        self.pentry.setEchoMode(QLineEdit.EchoMode.Password)
        self.pentry.setMinimumSize(400,30)
        # self.pentry.setStyleSheet(style)
        lm.addWidget(self.pentry, 3,0, alignment=centre)

        btn = QPushButton("submit")
        btn.clicked.connect(self.login_btn)
        lm.addWidget(btn, 4,0, alignment=centre|top)


    def login_btn(self):
        uname = self.uentry.text().strip()
        passwd = self.pentry.text().strip()
        if uname and passwd:
            self.uentry.clear()
            self.pentry.clear()
            print(f"username: {uname}\npassword: {passwd}")
            self.hide()
            mc = maincontainer(self.parent)
            self.layoutapp.addWidget(mc, 0,0)

        else:
            print("PLEASE ENTER USERNAME AND PASSWORD")
            return



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
 

class user_details(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.setStyleSheet("border: 1px solid orange; background-color: blue;")

        l = QLabel("userdetails")
        
        lud = QGridLayout(self)
        lud.addWidget(l)


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
        with open("Accident Prone Areas/accident_prone_areas.csv","r") as f:
            reader=csv.reader(f)
            next(reader)

            for row in reader:
                if row:
                    location_combo.addItem(row[1])
        result = location_combo.currentText()
        print(result)
        rptfl.addWidget(location_combo, 0,0, alignment=left)

        
        
        npa = QComboBox(reportf)
        npa.addItems()
        npa_result = npa.currentText()
        print(npa_result)
        # npa.setPlaceholderText("no. of people affected")
        # npa.setStyleSheet(styl)
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

app = App()
app.exec()