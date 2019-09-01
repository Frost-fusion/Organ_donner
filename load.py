import sys
from PyQt5 import QtWidgets, uic
import sqlite3


class test:
    def __init__(self):
        self.ui = uic.loadUi('organ.ui')
        self.ui.show()
        self.db()
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.log.clicked.connect(self.logit)
        self.ui.reg.clicked.connect(self.tabchange)

    def logit(self):
        global usr
        global psd
        self.ui.usr_name1.setText('')
        self.ui.usr_pass1.setText('')
        try:
            usr = self.ui.usr_name.text()
            psd = self.ui.usr_pass.text()
            if usr == "" and psd == "":
                raise Exception('both')
            if usr == "":
                raise Exception('usr')
            if psd == "":
                raise Exception('psd')
        except Exception as e:
            if str(e) == 'both':
                self.ui.usr_name1.setText('* UserName Required')
                self.ui.usr_pass1.setText('* Password Required')
            if str(e) == 'usr':
                self.ui.usr_name1.setText('* UserName Required')
            if str(e) == 'psd':
                self.ui.usr_pass1.setText('* Password Required')
        else:
            self.cur.execute('select * from login_id where usr_name = ? and password = ?',((usr),(psd)))
            chk = self.cur.fetchall()
            if chk:
                self.ui.statusbar.showMessage("Login Successful")
            else:
                self.ui.usr_name1.setText('Incorrect Username or Password')

    def db(self):
        try:
            self.conn = sqlite3.connect('organRecord')
            self.cur = self.conn.cursor()
            self.ui.statusbar.showMessage("Connected to Database")
            self.createdata()
        except Exception as e:
            print(e)
            self.ui.statusbar.showMessage(" Failed to Connect to Database:   Exiting Application")
            app.exit()

    def createdata(self):
        try:
            smt = "CREATE TABLE 'donor_data' ( `reg_no` TEXT NOT NULL UNIQUE, ` fname` TEXT, `mname` TEXT, `lname` TEXT, `dob` DATE, `Gender` NUMERIC, `Blood group` TEXT, `mob_no` INTEGER NOT NULL, `tele_no` INTEGER, `email` TEXT, `address` TEXT, `city` TEXT, `state` TEXT, `district` TEXT, `pin` NUMERIC,`pledge_date` DATE, `organ_donate` TEXT PRIMARY KEY(`reg_no`) );"
            self.cur.execute(smt)
            smt = "CREATE TABLE 'reciver_data' ( `reg_no` TEXT NOT NULL UNIQUE, ` fname` TEXT, `mname` TEXT, `lname` TEXT, `dob` DATE, `gender` INTEGER, `Blood group` TEXT, `mob_no.` INTEGER NOT NULL, `tele_no.` INTEGER, `email` TEXT, `address` TEXT,`city` TEXT, `state` TEXT, `district` TEXT, `pin` NUMERIC, `disease_of_patient ` TEXT, `examing_medical_consultant` TEXT, `Doctor_reg_no.` TEXT, `stage` TEXT, `priority ` TEXT, `transplant` TEXT, PRIMARY KEY(`reg_no`) );"
            self.cur.execute(smt)
            smt = "CREATE TABLE 'login_id' ( `usr_name` TEXT NOT NULL, `password` TEXT NOT NULL );"
            self.cur.execute(smt)
            self.cur.execute("INSERT INTO `login_id`(`usr_name`,`password`) VALUES ('Admin','Admin@00');")
        except Exception as a:
            st = str(a)
            st = st.find('already exists')
            if st ==-1:
                self.ui.statusbar.showMessage("Corrupted data in database")
            return

    def tabchange(self):
        self.ui.tabWidget.setCurrentIndex(1)


app = QtWidgets.QApplication(sys.argv)
win = test()
sys.exit(app.exec_())
