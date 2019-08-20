import sys
from PyQt5 import QtWidgets, uic
import sqlite3


class test:
    def __init__(self):
        self.ui = uic.loadUi('organ.ui')
        self.ui.show()
        self.db()
        self.ui.log.clicked.connect(self.logit)

    def logit(self):
        global usr
        global psd
        self.ui.usr_name1.setText('')
        try:
            usr = self.ui.usr_name.text()
            psd = self.ui.usr_pass.text()
            if usr == "" or psd == "":
                raise Exception
        except Exception as e:
            self.ui.usr_name1.setText('* UserName Required')
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
        except Exception as e:
            print(e)
            self.ui.statusbar.showMessage(" Failed to Connect to Database:   Exiting Application")
            app.exit()


app = QtWidgets.QApplication(sys.argv)
win = test()
sys.exit(app.exec_())
