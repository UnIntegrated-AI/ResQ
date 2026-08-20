from PySide6.QtWidgets import QFrame, QGridLayout, QComboBox, QLabel, QSpinBox, QPushButton
from PySide6.QtCore import Qt

class reportf(QFrame):
    def __init__(self,parent):
        super().__init__(parent)
        self.setStyleSheet("QFrame{border: 1px solid orange;}")
        rptfl = QGridLayout(self)

        rptfl.setRowStretch(0,1)
        rptfl.setRowStretch(1,1)
        rptfl.setRowStretch(2,1)

        rptfl.setColumnStretch(0,3)
        rptfl.setColumnStretch(1,5)

        self.setStyleSheet("""
            QFrame{
                background-color: whitesmoke;
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
        """)

        #Location thing
        location_heading = QLabel("Location of Incident")
        rptfl.addWidget(location_heading, 0,0)

        self.location_combo = QComboBox(self)
        # with open(r"C:\Users\yadav\OneDrive\Desktop\Ansh\New folder\Accident Prone Areas\accident_prone_areas.csv","r") as f:
        #     reader = csv.reader(f)
        #     next(reader)
        reader = ["hello", "world", "wow","nice"]
        for row in reader:
            self.location_combo.addItem(row)
        rptfl.addWidget(self.location_combo, 0,1)

        #no. of pepole affected thing 
        npa_heading = QLabel("No. of people affected")
        rptfl.addWidget(npa_heading, 1,0)
        
        self.npa = QSpinBox(self)
        self.npa.setMinimum(1) 
        self.npa.setMaximum(100) 
        rptfl.addWidget(self.npa, 1,1)

        # type of accident thing
        taccd_heading = QLabel("Type of Incident") 
        rptfl.addWidget(taccd_heading, 2,0) 

        type_of_accidents = ["Road Accident", "Landslide", "Fuel", "Motor support"]

        self.taccd = QComboBox(self)
        for a in type_of_accidents: 
            self.taccd.addItem(a)
        rptfl.addWidget(self.taccd, 2,1) 

        # submit button

        report_btn = QPushButton("Report", self)
        rptfl.addWidget(report_btn,3,0,1,2,alignment=Qt.AlignmentFlag.AlignHCenter) 
        report_btn.clicked.connect(self.report_func)

    def report_func(self):
        location = self.location_combo.currentData()
        npa = self.npa.value()
        taccd = self.taccd.currentData()

        print(f"location:{location}\nno. of pepole affected:{npa}\ntype of incident:{taccd}")