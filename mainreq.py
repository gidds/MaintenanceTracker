import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sqlite3, os, csv, datetime, logging

#database global variables for locations

REQUISITIONS_DB =  None
JOBCARDS_DB = None

class MaintenanceTracker(QWidget):
    
    def create_requisitions_db(self,db_folder):
        global REQUISITIONS_DB

        # Create the database folder if it doesn't exist
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)

        #set the path to the database
        REQUISITIONS_DB = os.path.join(db_folder, "requisitions.db")

        #Create the databases if they don't exist
        print
        if not os.path.exists(REQUISITIONS_DB):
            conn = sqlite3.connect(REQUISITIONS_DB)
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS requisitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE,
                work_request TEXT,
                requested_by TEXT,
                date_created TEXT DEFAULT CURRENT_DATE,
                date_last_modified TEXT DEFAULT CURRENT_DATE    
            )
        ''')
            print("Database and tables created for Requisitions")
            conn.commit()
            conn.close()
    
    def create_jobcards_db(self,db_folder):
        global JOBCARDS_DB

        if not os.path.exists(db_folder):
            os.makedirs(db_folder)

        JOBCARDS_DB = os.path.join(db_folder, "jobcards.db")
        if not os.path.exists(JOBCARDS_DB):
            conn = sqlite3.connect(JOBCARDS_DB)
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE,
                date_created TEXT DEFAULT CURRENT_DATE,
                date_last_modified TEXT DEFAULT CURRENT_DATE,
                requisition_id INTEGER,
                work_request TEXT,
                time_start TEXT,
                time_stop TEXT,
                time_diff TEXT,
                artisan TEXT,
                machine TEXT,
                department TEXT,
                apprentice TEXT,
                typeoffault TEXT,
                FOREIGN KEY (requisition_id) REFERENCES requisitions(id)
                )
            ''')
            print("Database and tables created for Jobcards")
            conn.commit()
            conn.close()
        
#setup save button for tab2 to save work request to database
    def insert_requisition(self):
        req_num = self.reqnum_input_tab2.text()
        work_request = self.work_request_input.toPlainText()
        requested_by = self.reqwho_input.text()
        date_created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_last_modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn_req = sqlite3.connect(REQUISITIONS_DB)
        cursor_req = conn_req.cursor()
        cursor_req.execute('''
            INSERT INTO requisitions (number, work_request, requested_by, date_created, date_last_modified)
            VALUES (?, ?, ?, ?, ?)
            ''', (req_num, work_request, requested_by, date_created, date_last_modified))
        conn_req.commit()
        conn_req.close()

    def insert_jobcard(self):
        jobcard_num = self.jobcard_num_input.text()
        reqnum = self.reqnum_combobox.currentText()
        work_request = self.work_request_jinput.toPlainText()
        time_start = self.time_start_input.text()
        time_stop = self.time_stop_input.text()
        time_diff = self.time_taken_label.text()
        date_created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_last_modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        artisan = self.artisan_input.currentText()
        machine = self.machine_input.currentText()
        department = self.department_input.currentText()
        apprentice = self.apprentice_input.currentText()
        typeoffault = self.type_of_fault_input.currentText()

        conn_job = sqlite3.connect(JOBCARDS_DB)
        cursor_job = conn_job.cursor()
        cursor_job.execute('''
            INSERT INTO jobcards (number, work_request, time_start, time_stop, time_diff, date_created, date_last_modified, requisition_id, artisan, machine, department, apprentice, typeoffault)
            VALUES (?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?)
            ''', (jobcard_num, work_request, time_start, time_stop, time_diff, date_created, date_last_modified, reqnum, artisan, machine, department, apprentice, typeoffault))
        conn_job.commit()
        conn_job.close()

        conn_req = sqlite3.connect(REQUISITIONS_DB)
        cursor_req = conn_req.cursor()
        cursor_req.execute("Delete FROM requisitions WHERE number = ?", (reqnum,))
        conn_req.commit()
        conn_req.close()
        

    def save_requisition(self):
        self.insert_requisition()
        self.reqnum_combobox.clear()
        self.populate_combobox()
        self.work_request_input.clear()
        self.reqwho_input.clear()

    def save_jobcard(self):
        self.insert_jobcard()
        self.jobcard_num_input.clear()
        self.time_start_input.clear()
        self.time_stop_input.clear()
        self.artisan_input.clear()
        self.machine_input.clear()
        self.department_input.clear()
        self.apprentice_input.clear()
        self.type_of_fault_input.clear()
        self.time_taken_label.setText("Time Taken : 00:00:00")

    def populate_combobox(self):
        conn = sqlite3.connect(REQUISITIONS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT number FROM requisitions")
        rows = cursor.fetchall()
        self.reqnum_combobox.clear()
        for number in rows:
            self.reqnum_combobox.addItem(number[0])
        conn.close()

    def populate_work_request(self):
        self.work_request_jinput.clear()
        reqnum = self.reqnum_combobox.currentText()
        self.requested_by_jinput.clear()
        conn = sqlite3.connect(REQUISITIONS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT work_request FROM requisitions WHERE number = ?", (reqnum,))
        rowswork = cursor.fetchall()
        for work_request in rowswork:
            self.work_request_jinput.append(work_request[0])
        cursor.execute("SELECT requested_by FROM requisitions WHERE number = ?", (reqnum,))
        rowswho = cursor.fetchall()
        for requested_by in rowswho:
            self.requested_by_jinput.setText(requested_by[0])
        
        conn.close()

    def populate_departments(self):
        self.department_input.clear()
        with open("csv/department.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                self.department_input.addItem(row[0])

    def populate_machines(self):
        self.machine_input.clear()
        with open("csv/machines.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                self.machine_input.addItem(row[0])
    
    def populate_artisans(self):
        self.artisan_input.clear()
        with open("csv/artisans.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                self.artisan_input.addItem(row[0])
    
    def populate_apprentices(self):
        self.apprentice_input.clear()
        with open("csv/apprentice.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                self.apprentice_input.addItem(row[0])
    
    def populate_typeoffault(self):
        self.type_of_fault_input.clear()
        with open("csv/typeoffault.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                self.type_of_fault_input.addItem(row[0])
    


    def __init__(self):
        super().__init__()

        db_folder = os.path.join(os.getcwd(),"db_folder")
        self.create_requisitions_db(db_folder)
        self.create_jobcards_db(db_folder)
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.addTab(self.tab1, "Log Jobcards")
        self.tabs.addTab(self.tab2, "Log Requisitions")

        # Tab 1 layout
        tab1grid_layout = QGridLayout()
        self.tab1.setLayout(tab1grid_layout)

        tab1grid_layout.setColumnStretch(0, 1)
        tab1grid_layout.setColumnStretch(1, 1)
        tab1grid_layout.setColumnStretch(2, 1)
        tab1grid_layout.setColumnStretch(3, 1)

        label = QLabel("Maintenance Tracker")
        tab1grid_layout.addWidget(label, 0, 0, 1, 4)

        #Requisition number
        reqnum_label = QLabel("Requisition Number:")
        self.reqnum_combobox = QComboBox()
        tab1grid_layout.addWidget(reqnum_label, 1, 0)
        tab1grid_layout.addWidget(self.reqnum_combobox, 1, 1)
        

        #Jobcard number
        jobcard_num_label = QLabel("Jobcard Number:")
        self.jobcard_num_input = QLineEdit()
        tab1grid_layout.addWidget(jobcard_num_label, 1, 2)
        tab1grid_layout.addWidget(self.jobcard_num_input, 1, 3)

        #Requested by
        requested_by_label = QLabel("Requested By:")
        self.requested_by_jinput = QLineEdit()
        tab1grid_layout.addWidget(requested_by_label, 2, 0)
        tab1grid_layout.addWidget(self.requested_by_jinput, 2, 1)

        #Date requested display
        date_requested_label = QLabel("Date Requested:")
        self.date_requested_input = QDateEdit()
        self.date_requested_input.setDisplayFormat("yyyy-MM-dd")
        self.date_requested_input.setDate(QDate.currentDate())
        tab1grid_layout.addWidget(date_requested_label, 2, 2)
        tab1grid_layout.addWidget(self.date_requested_input, 2, 3)

        #Time start selection with time picker
        time_start_label = QLabel("Time Start:")
        self.time_start_input = QTimeEdit()
        self.time_start_input.setDisplayFormat("hh:mm")
        self.time_start_input.setTime(QTime(8,0,0))
        tab1grid_layout.addWidget(time_start_label, 3, 0)
        tab1grid_layout.addWidget(self.time_start_input, 3, 1)

        #Time stop selection with time picker
        time_stop_label = QLabel("Time Stop:")
        self.time_stop_input = QTimeEdit()
        self.time_stop_input.setDisplayFormat("hh:mm")
        self.time_stop_input.setTime(QTime(8,0,0))
        tab1grid_layout.addWidget(time_stop_label, 3, 2)
        tab1grid_layout.addWidget(self.time_stop_input, 3, 3)

        #Select Department ComboBox
        department_label = QLabel("Department:")
        self.department_input = QComboBox()
        tab1grid_layout.addWidget(department_label, 4, 0)
        tab1grid_layout.addWidget(self.department_input, 4, 1)

        #Select Machine ComboBox
        machine_label = QLabel("Machine:")
        self.machine_input = QComboBox()
        tab1grid_layout.addWidget(machine_label, 4, 2)
        tab1grid_layout.addWidget(self.machine_input, 4, 3)

        #create form layout for work done
        tab1form_layout = QFormLayout()
        tab1grid_layout.addLayout(tab1form_layout, 5, 0, 1, 4)

        # Textbox to receive requested work information
        work_request_label = QLabel("Work Request / Fault Description:")
        tab1form_layout.addRow(work_request_label)
        self.work_request_jinput = QTextEdit()
        tab1form_layout.addRow(self.work_request_jinput)

        # Textbox to receive work carried out
        work_done_label = QLabel("Work Carried Out:")
        tab1form_layout.addRow(work_done_label)
        self.work_done_input = QTextEdit()
        tab1form_layout.addRow(self.work_done_input)

        #Type of Fault Combobox
        type_of_fault_label = QLabel("Type of Fault:")
        self.type_of_fault_input = QComboBox()
        tab1form_layout.addRow(type_of_fault_label, self.type_of_fault_input)

        #Artisan ComboBox
        artisan_label = QLabel("Artisan:")
        self.artisan_input = QComboBox()
        tab1form_layout.addRow(artisan_label, self.artisan_input)

        #Apprentice ComboBox
        apprentice_label = QLabel("Apprentice:")
        self.apprentice_input = QComboBox()
        tab1form_layout.addRow(apprentice_label, self.apprentice_input)

        #label to show time taken calculated from time stop and time start
        self.time_taken_label = QLabel("Time Taken: 00:00:00")
        tab1form_layout.addRow(self.time_taken_label)
        self.time_stop_input.timeChanged.connect(self.calculate_time)
        

        #save button
        save_button = QPushButton("Save")
        #change button width and centre
        save_button.setFixedWidth(100)
        tab1form_layout.addRow(save_button)

        save_button.clicked.connect(lambda: [self.save_jobcard(), self.populate_combobox(), self.populate_apprentices(), self.populate_machines(), self.populate_departments(), self.populate_artisans()])

        # Tab 2 layout
        tab2_layout = QGridLayout()
        self.tab2.setLayout(tab2_layout)

        label = QLabel("Requisition Tracker")
        tab2_layout.addWidget(label, 0, 0, 1, 4)

        reqnum_label = QLabel("Requisition Number:")
        self.reqnum_input_tab2 = QLineEdit()
        tab2_layout.addWidget(reqnum_label, 1, 0)
        tab2_layout.addWidget(self.reqnum_input_tab2, 2, 0)

        reqwho_label = QLabel("Requested By:")
        self.reqwho_input = QLineEdit()
        tab2_layout.addWidget(reqwho_label, 1, 1)
        tab2_layout.addWidget(self.reqwho_input, 2, 1)

        work_request_label = QLabel("Work Request:")
        self.work_request_input = QTextEdit()
        tab2_layout.addWidget(work_request_label, 3, 0, 1, 2)
        tab2_layout.addWidget(self.work_request_input, 4, 0, 1, 2)

        save_button_tab2 = QPushButton("Save")
        save_button_tab2.setFixedWidth(100)
        tab2_layout.addWidget(save_button_tab2, 5, 0,)
        save_button_tab2.clicked.connect(self.save_requisition)

        main_layout = QGridLayout()
        main_layout.addWidget(self.tabs, 0, 0)
        self.setLayout(main_layout)

         # Get the screen size
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Set the window size to % of the screen size
        window_width = int(screen_width * 0.45)
        window_height = int(screen_height * 0.75)
        self.resize(window_width, window_height)

        # Center the window on the screen
        self.move((screen_width - window_width) // 2, (screen_height - window_height) // 2)

        self.populate_combobox()
        self.populate_work_request()
        self.reqnum_combobox.currentIndexChanged.connect(self.populate_work_request)


        self.time_start_input.timeChanged.connect(self.calculate_time)
        self.time_stop_input.timeChanged.connect(self.calculate_time)

        self.populate_departments()
        self.populate_machines()
        self.populate_artisans()
        self.populate_apprentices()
        self.populate_typeoffault()
    def calculate_time(self):
        time_start = self.time_start_input.time()
        time_stop = self.time_stop_input.time()
        if time_stop < time_start:
            self.time_stop_input.setTime(time_start)
            time_stop = self.time_stop_input.time()
        time_diff = abs(time_stop.secsTo(time_start))
        hours = time_diff // 3600
        minutes = (time_diff % 3600) // 60
        seconds = time_diff % 60
        time_diff_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.time_taken_label.setText(str("Time Taken: " + time_diff_string))
    
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Maintenance Tracker and Requisition Logger")
    window = MaintenanceTracker()
    window.show()
    sys.exit(app.exec_())