import socket
import json
import csv
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QGridLayout,
    QFrame,
    QLineEdit,
    QPushButton,
    QComboBox,
    QSpinBox,
    QScrollArea,
)
from PySide6.QtCore import Qt
import webbrowser
import asyncio
from winrt.windows.devices.geolocation import (
    Geolocator,
    PositionAccuracy,
    GeolocationAccessStatus,
)
import sys
import os

HOST = "127.0.0.1"
PORT = 4848
CREW = None
UNAME = None

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

centre = Qt.AlignmentFlag.AlignCenter
top = Qt.AlignmentFlag.AlignTop
bottom = Qt.AlignmentFlag.AlignBottom
left = Qt.AlignmentFlag.AlignLeft
right = Qt.AlignmentFlag.AlignRight


def open_map(lat, lon):
    webbrowser.open(f"https://google.com/maps?q={lat},{lon}")


async def get_location():
    # Ask Windows for permission
    access = await Geolocator.request_access_async()

    if access != GeolocationAccessStatus.ALLOWED:
        print("Location permission denied:", access)
        return

    # Create location provider
    locator = Geolocator()

    # Ask for high accuracy
    locator.desired_accuracy = PositionAccuracy.HIGH

    # Get current position
    position = await locator.get_geoposition_async()

    coordinate = position.coordinate

    print("Latitude :", coordinate.latitude)
    print("Longitude:", coordinate.longitude)
    print("Accuracy :", coordinate.accuracy, "meters")

    coords = [coordinate.latitude, coordinate.longitude, coordinate.accuracy]

    return coords


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def send_packet(sock, packet):
    data = json.dumps(packet).encode()
    length = len(data).to_bytes(4, "big")
    sock.sendall(length + data)


def recv_packet(sock):
    header = recv_exact(sock, 4)

    if not header:
        return None

    length = int.from_bytes(header, "big")
    data = recv_exact(sock, length)

    if not data:
        return None

    return json.loads(data.decode())


class App(QApplication):
    def __init__(self):
        super().__init__()

        self.window = QWidget()

        self.window.resize(800, 500)
        self.window.setWindowTitle("ResQ")

        layout = QGridLayout(self.window)

        lf = loginframe(self.window, layout,self)

        layout.addWidget(lf, 0, 0)

        self.window.show()


class user_details(QFrame):
    def __init__(self, parent,lf,app):
        super().__init__(parent)
        self.parent = parent
        self.lf = lf
        self.app = app

        self.setStyleSheet("""
            QFrame{
                background-color: #fff2cc;
                color: black;
                border: 1px solid #DC2626;
                border-radius: 8px;
                padding: 11px;
            }
            QLabel{
                border: none;
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton{
                background-color: red;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 11px;
                font-size: 15px;
                font-weight: bold;
            }
        """)
        lud = QGridLayout(self)
        l = QLabel(f"Username:\t{UNAME}")
        lud.addWidget(l, 0, 0, alignment=centre|top)

        t = QLabel(f"Type:\t{CREW}")
        lud.addWidget(t, 1, 0, alignment=centre|top)

        logout = QPushButton("Logout")
        lud.addWidget(logout, 2,0, alignment=bottom)
        lud.setRowStretch(0,1)
        lud.setRowStretch(1,1)
        lud.setRowStretch(2,5)
        logout.clicked.connect(self.signout)

    def signout(self):
        self.parent.hide()
        self.lf.show()
        send_packet(client, {"type":"logout"} )
        self.app.quit()
        os.execv(sys.executable, [sys.executable]+sys.argv)
        

class maincontainer(QFrame):
    def __init__(self, parent,app):
        super().__init__(parent)
        self.setStyleSheet("background-color: #fff2cc;")

        lmc = QGridLayout(self)

        udf = user_details(self,parent,app)
        lmc.addWidget(udf, 0, 1)
        if CREW == "Crew":
            mff = mainframe_crew(self)
            lmc.addWidget(mff, 0, 0)
        else:
            mff = mainframe_user(self)
            lmc.addWidget(mff, 0, 0)
        

        lmc.setColumnStretch(0, 3)
        lmc.setColumnStretch(1, 1)


class mainframe_crew(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.widget = QWidget()
        self.setWidget(self.widget)
        self.setWidgetResizable(True)
        self.display_reports()

    def display_reports(self):
        reports = self.get_reports()


        self.widget = QWidget()
        self.setWidget(self.widget)

        self.mrl = QGridLayout(self.widget)
        self.setStyleSheet(""" 
            QFrame{  
                border: 1px solid #DC2626;
                border-radius: 8px;
            }
            QLabel{
                border: none;
                color: black;
                font-size: 11px;
                font-weight: bold;
            } 
            QPushButton{
                background-color: #dc6426;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 11px;
                font-size: 15px;
                font-weight: bold;
            } 
            """)

        for a in range(len(reports)):
            rf = QFrame(self.widget)
            self.mrl.addWidget(rf, a, 0)
            fl = QGridLayout(rf)
            locl = QLabel(f"Location:\t{str(reports[a][0])}")
            fl.addWidget(locl, 0, 0, alignment=left)
            npal = QLabel(f"No. of People affected:\t{str(reports[a][1])}")
            fl.addWidget(npal, 1, 0, alignment=left)
            taccdl = QLabel(f"Type of Incident:\t{str(reports[a][2])}")
            fl.addWidget(taccdl, 2, 0, alignment=left)
            stsl = QLabel("Status:\tOpen" if str(reports[a][3]) == "1" else "Status:\tClosed")
            fl.addWidget(stsl, 3, 0, alignment=left)

            tkac = QPushButton("take action")
            fl.addWidget(tkac, 4,0,alignment=right|bottom)
            tkac.clicked.connect(lambda checked=False, k=reports[a][0]: self.openmap(k))

            fl.setRowStretch(0,1)
            fl.setRowStretch(1,1)
            fl.setRowStretch(2,1)
            fl.setRowStretch(3,1)
            fl.setRowStretch(4,2)

    def openmap(self,locl):
        locl = locl[1:]
        locl = locl.split(",")

        print(f"{locl[0].strip(), locl[1].strip()}")
        print(f"{locl} ka map laga do")
        open_map(locl[0],locl[1])

    def get_reports(self):
        result = []
        send_packet(client, {"type": "view_reports"})
        result = recv_packet(client)
        return result["reports"]



class mainframe_user(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.lmf = QGridLayout(self)

        self.setStyleSheet("""
            QPushButton{
                background-color: #DC2626;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 11px;
                font-size: 15px;
                font-weight: bold;
            }
        """)

        nav_container = QFrame(self)
        ncl = QGridLayout(nav_container)
        nav_container.setStyleSheet(
            "QFrame{border: 1px solid #DC2626; border-radius: 8px;}"
        )
        self.lmf.addWidget(nav_container, 0, 0, alignment=top)

        report_btn = QPushButton("Report an Accident", nav_container)
        report_btn.clicked.connect(self.report)
        ncl.addWidget(report_btn, 0, 0)

        yreports_btn = QPushButton("My Reports", nav_container)
        yreports_btn.clicked.connect(self.myreports)
        ncl.addWidget(yreports_btn, 0, 1)

        ncl.setAlignment(centre | left)
        self.lmf.setRowStretch(0, 0)
        self.lmf.setRowStretch(1, 1)

        self.reportframe = self.reportf(self)
        self.lmf.addWidget(self.reportframe, 1, 0)
        self.reportframe.hide()

        self.myreportsframe = self.myreportsf(self)
        self.lmf.addWidget(self.myreportsframe, 1, 0)
        self.myreportsframe.hide()

    class reportf(QFrame):
        def __init__(self, parent):
            super().__init__(parent)
            self.setStyleSheet("QFrame{border: 1px solid #DC2626; border-radius: 8px;}")
            rptfl = QGridLayout(self)

            rptfl.setRowStretch(0, 1)
            rptfl.setRowStretch(1, 1)
            # rptfl.setRowStretch(2, 1)

            rptfl.setColumnStretch(0, 3)
            rptfl.setColumnStretch(1, 5)

            self.setStyleSheet("""
            QFrame{
                border: 1px solid #DC2626;
                border-radius: 8px;
                background-color: #fff2cc;
                color: black
            }
            QPushButton{
                background-color: #DC2626;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 11px;
                font-size: 15px;
                font-weight: bold;
            }
            QSpinBox{
                background-color: #fff2cc;
                color: black;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QComboBox{
                background-color: #fff2cc;
                color: black;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLabel{
                color: black;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
         """)

            # Location thing
            # location_heading = QLabel("Location of Incident")
            # rptfl.addWidget(location_heading, 0, 0)

            npa_heading = QLabel("No. of people affected")
            rptfl.addWidget(npa_heading, 0, 0)

            self.npa = QSpinBox(self)
            self.npa.setMinimum(1)
            self.npa.setMaximum(100)
            rptfl.addWidget(self.npa, 0, 1)

            # type of accident thing
            taccd_heading = QLabel("Type of Incident")
            rptfl.addWidget(taccd_heading, 1, 0)

            type_of_accidents = ["Road Accident", "Landslide", "Fuel", "Motor support"]

            self.taccd = QComboBox(self)
            for a in type_of_accidents:
                self.taccd.addItem(a)
            rptfl.addWidget(self.taccd, 1, 1)

            # submit button

            report_btn = QPushButton("Report", self)
            rptfl.addWidget(
                report_btn, 2, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignHCenter
            )
            report_btn.clicked.connect(self.report_func)

        def report_func(self):
            coords = asyncio.run(get_location())
            npa = self.npa.value()
            taccd = self.taccd.currentText()
            send_packet(
                client,
                {"type": "new_report", "location": coords, "npa": npa, "taccd": taccd},
            )
            print(
                f"location:{coords}\nno. of pepole affected:{npa}\ntype of incident:{taccd}"
            )

    def report(self):
        self.myreportsframe.hide()
        self.reportframe.show()

    class myreportsf(QScrollArea):
        def __init__(self, parent):
            super().__init__(parent)
            self.widget = QWidget()
            self.setWidget(self.widget)
            self.setWidgetResizable(True)
            self.display_reports()

        def display_reports(self):
            reports = self.get_reports()

            old_widget = self.widget
            old_widget.deleteLater()

            self.widget = QWidget()
            self.setWidget(self.widget)

            self.mrl = QGridLayout(self.widget)
            self.setStyleSheet(""" 
                QFrame{  
                    border: 1px solid #D1D5DB;
                    border-radius: 8px;
                }
                QLabel{
                    border: none;
                    color: black;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton{
                    background-color: #dc6426;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 11px;
                    font-size: 15px;
                    font-weight: bold;
                }
                """)

            for a in range(len(reports)):
                rf = QFrame(self.widget)
                self.mrl.addWidget(rf, a, 0)
                fl = QGridLayout(rf)
                locl = QLabel(str(reports[a][0]))
                fl.addWidget(locl, 0, 0, alignment=left)
                npal = QLabel(str(reports[a][1]))
                fl.addWidget(npal, 1, 0, alignment=left)
                taccdl = QLabel(str(reports[a][2]))
                fl.addWidget(taccdl, 2, 0, alignment=left)
                stsl = QLabel("Open" if str(reports[a][3]) == "1" else "Closed")
                fl.addWidget(stsl, 3, 0, alignment=left)

        def get_reports(self):
            result = []
            send_packet(client, {"type": "view_reports"})
            result = recv_packet(client)
            return result["reports"]

    def myreports(self):
        self.myreportsframe.display_reports()
        self.myreportsframe.show()
        self.reportframe.hide()


class loginframe(QFrame):
    def __init__(self, parent, layoutapp,app):
        super().__init__(parent)

        self.parent = parent
        self.layoutapp = layoutapp
        self.app = app

        self.setStyleSheet("""
            QFrame {
                background-color: #fff2cc;
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

            QComboBox{
                background-color: #fff2cc;
                color: black;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }

            QLineEdit {
                background-color: #fff2cc;
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


        title = QLabel("ResQ")
        title.setObjectName("title")
        title.setAlignment(centre)
        layout.addWidget(title, 0, 0)

        subtitle = QLabel("Emergency Response & Reporting")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(centre)
        layout.addWidget(subtitle, 1, 0)

        self.uentry = QLineEdit()
        self.uentry.setPlaceholderText("Username")
        self.uentry.setFixedSize(350, 45)
        layout.addWidget(self.uentry, 3, 0)

        self.pentry = QLineEdit()
        self.pentry.setPlaceholderText("Password")
        self.pentry.setEchoMode(QLineEdit.EchoMode.Password)
        self.pentry.setFixedSize(350, 45)
        layout.addWidget(self.pentry, 4, 0)

        self.cou = QComboBox(self)
        layout.addWidget(self.cou, 5, 0)
        self.cou.addItems(["User", "Crew"])


        reg_log_btn = QPushButton("LOGIN/Register")
        reg_log_btn.setFixedSize(350, 45)
        reg_log_btn.clicked.connect(self.login_btn)
        layout.addWidget(reg_log_btn, 7, 0)

        layout.setSpacing(15)
        layout.setSpacing(10)

    def login_btn(self):
        uname = self.uentry.text().strip()
        passwd = self.pentry.text().strip()
        crew = self.cou.currentText()

        if uname and passwd:
            global CREW, UNAME
            CREW = crew
            UNAME = uname
            print(f"username: {uname}")
            print(f"password: {passwd}")
            send_packet(
                client,
                {
                    "type": "login_details",
                    "uname": uname,
                    "passwd": passwd,
                    "crew": crew,
                },
            )
            packet = recv_packet(client)
            crew = packet["crew"]
            self.uentry.clear()
            self.pentry.clear()

            self.hide()
            mc = maincontainer(self,self.app)
            self.layoutapp.addWidget(mc, 0, 0)
        else:
            print("Enter Username and Password")
            return


app = App()
app.exec()
