import datetime
import re
import sqlite3
import sys

from PyQt5.QtWidgets import QMessageBox, QVBoxLayout
from PyQt5 import QtWidgets, uic


class Test:
    cursor: sqlite3.Cursor

    def __init__(self):
        self.ui = uic.loadUi('organ.ui')
        self.ui.show()
        self.create_database()
        self.ui.mainTab.setCurrentIndex(0)
        self.ui.changeLoginTypeStack.setCurrentIndex(0)
        self.ui.changeFormStack.setCurrentIndex(0)
        self.ui.adminLoginStackTab.setCurrentIndex(0)
        self.ui.loginButton.clicked.connect(self.login)
        self.ui.homeTabRegisterButton.clicked.connect(self.tab_change)
        self.ui.formSelecter.currentIndexChanged.connect(self.change_form)
        self.ui.registerTabRegisterButton.clicked.connect(self.add_record)
        self.ui.renewApplicationButton.clicked.connect(self.renew_application)
        self.ui.goToLoginPageReceiver.clicked.connect(self.set_login_page)
        self.ui.goToLoginPageDonor.clicked.connect(self.set_login_page)
        self.ui.goToLoginPageAdmin.clicked.connect(self.set_login_page)
        self.ui.forgotPasswordButton.clicked.connect(password_reset)
        self.ui.adminLoginStackTab.currentChanged.connect(self.populate_record)
        self.ui.searchRecord.clicked.connect(self.admin_populate)
        self.ui.deleteRecord.clicked.connect(delete_record)
        self.ui.updateRecord.clicked.connect(update_record)

    def login(self):
        user_name: str
        password: str
        self.ui.statusNameLabel.setText('')
        self.ui.statusPasswordLabel.setText('')
        try:
            user_name = self.ui.userName.text()
            password = self.ui.userPassword.text()
            if user_name == "" and password == "":
                raise Exception('both')
            if user_name == "":
                raise Exception('user_name')
            if password == "":
                raise Exception('password')
        except Exception as e:
            if str(e) == 'both':
                self.ui.statusNameLabel.setText('* UserName Required')
                self.ui.statusPasswordLabel.setText('* Password Required')
            if str(e) == 'user_name':
                self.ui.statusNameLabel.setText('* UserName Required')
            if str(e) == 'password':
                self.ui.statusPasswordLabel.setText('* Password Required')
        else:
            check = None
            if 'Admin' in user_name:
                self.cursor.execute('select * from loginId where username = ? and password = ?;',
                                    (user_name, password))
                check = self.cursor.fetchall()
                if check:
                    self.populate_record()
                    self.ui.changeLoginTypeStack.setCurrentIndex(1)
            elif 'REC' in user_name:
                self.cursor.execute('select * from loginId where userName = ? and password = ?;',
                                    (user_name, password))
                check = self.cursor.fetchall()
                if check:
                    self.ui.changeLoginTypeStack.setCurrentIndex(3)
                    self.populate_receiver(user_name)
            elif 'DON' in user_name:
                self.cursor.execute('select * from loginId where userName = ? and password = ?;',
                                    (user_name, password))
                check = self.cursor.fetchall()
                if check:
                    self.ui.changeLoginTypeStack.setCurrentIndex(2)
            else:
                self.ui.statusNameLabel.setText('Incorrect Username or Password')

    def create_database(self):
        try:
            self.connection = sqlite3.connect('organRecord.db')
            self.cursor = self.connection.cursor()
            self.create_data()
            self.ui.statusbar.showMessage("Connected to Database")
        except Exception as e:
            print(e)
            self.ui.statusbar.showMessage(" Failed to Connect to Database:   Exiting Application")
            app.exit()

    def create_data(self):
        try:
            query = """CREATE TABLE IF NOT EXISTS donor(registrationNumber VARCHAR(5), firstName VARCHAR(20),
                    middleName VARCHAR(20), lastName VARCHAR(20), dateOfBirth DATE, gender VARCHAR(10), 
                    bloodGroup  VARCHAR(3), mobileNumber VARCHAR(15), landLineNumber VARCHAR(15), email VARCHAR(100),
                    address VARCHAR(255), city VARCHAR(30), district VARCHAR(30), state varchar(30), pinCode VARCHAR(6),
                    pledgeDate DATE,donatingOrgans VARCHAR(100));"""
            self.cursor.execute(query)
            self.connection.commit()
            query = """CREATE TABLE IF NOT EXISTS receiver(registrationNumber VARCHAR(5), firstName VARCHAR(20),
                    middleName VARCHAR(20), lastName VARCHAR(20), dateOfBirth DATE, gender VARCHAR(10), 
                    bloodGroup  VARCHAR(3), mobileNumber VARCHAR(15), landLineNumber VARCHAR(15), email VARCHAR(100),
                    address VARCHAR(255), city VARCHAR(30), district VARCHAR(30),state varchar(30), pinCode VARCHAR(6),
                    disease VARCHAR(50),doctorName VARCHAR(50), doctorRegistration VARCHAR(30), illnessStage VARCHAR(15)
                    ,priority VARCHAR(20),transplantingOrgan VARCHAR(10));"""
            self.cursor.execute(query)
            self.connection.commit()
            query = """CREATE TABLE IF NOT EXISTS loginId(userName varchar(10),password varchar(10));"""
            self.cursor.execute(query)
            query = """SELECT * FROM loginId;"""
            self.cursor.execute(query)
            if not self.cursor.fetchone():
                query = """INSERT INTO loginId(userName, password) values('Admin','Admin@0');"""
                self.cursor.execute(query)
                self.connection.commit()
        except Exception as e:
            print(e)

    def tab_change(self):
        self.ui.mainTab.setCurrentIndex(1)

    def set_login_page(self):
        self.ui.changeLoginTypeStack.setCurrentIndex(0)
        self.ui.userName.clear()
        self.ui.userPassword.clear()

    def add_record(self):
        if self.ui.formSelecter.currentIndex() == 0:
            data = []
            registration_number = 'DON1'
            self.cursor.execute("select registrationNumber from donor;")
            if self.cursor.fetchone():
                self.cursor.execute("select registrationNumber from donor ORDER BY registrationNumber DESC LIMIT 1;")
                old_registration_number = self.cursor.fetchone()
                registration_number = int(re.search(r'\d', old_registration_number[0]).group())
                registration_number = 'DON' + str(registration_number + 1)
            data.append(registration_number)
            data.append(self.ui.fristName.text())
            data.append(self.ui.middleName.text())
            data.append(self.ui.lastName.text())
            date_of_birth = self.ui.dateOfBirth.date().toPyDate()
            data.append(date_of_birth.strftime("%d-%m-%Y"))
            if self.ui.radioFemale.isChecked():
                data.append('Female')
            if self.ui.radioMale.isChecked():
                data.append('Male')
            else:
                data.append('Other')
            data.append(self.ui.bloodGroup.currentText())
            data.append(self.ui.mobileNumber.text())
            data.append(self.ui.landLineNumber.text())
            data.append(self.ui.email.text())
            data.append(self.ui.permanantAddress.toPlainText())
            data.append(self.ui.addCity.text())
            data.append(self.ui.addState.currentText())
            data.append(self.ui.addDistrict.text())
            data.append(self.ui.addPincode.text())
            pledge_date = datetime.datetime.now()
            data.append(pledge_date.strftime("%d-%m-%Y-%I-%M-%p"))
            donate = ''
            if self.ui.donateBody.isChecked():
                donate = donate + 'Body'
            if self.ui.donateEyes.isChecked():
                donate = donate + 'Eyes'
            if self.ui.donateKidney.isChecked():
                donate = donate + 'Kidney'
            if self.ui.donatePancreas.isChecked():
                donate = donate + 'Pancreas'
            if self.ui.donateHeart.isChecked():
                donate = donate + 'Heart'
            if self.ui.donateLungs.isChecked():
                donate = donate + 'Lungs'
            data.append(donate)
            query = """INSERT INTO donor(registrationNumber , firstName ,middleName , lastName ,
                        dateOfBirth , gender , bloodGroup , mobileNumber , landLineNumber , email ,
                        address , city , district ,state, pinCode , pledgeDate ,donatingOrgans) 
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""
            self.cursor.execute(query, data)
            self.connection.commit()
            self.ui.statusbar.showMessage("Added Record")
            response = add_sucess()
            if response:
                self.renew_application()
        if self.ui.formSelecter.currentIndex() == 1:
            data = []
            registration_number = 'DON1'
            self.cursor.execute("select registrationNumber from receiver;")
            if self.cursor.fetchone():
                self.cursor.execute("select registrationNumber from receiver ORDER BY registrationNumber DESC LIMIT 1;")
                old_registration_number = self.cursor.fetchone()
                registration_number = int(re.search(r'\d+', old_registration_number[0]).group())
                registration_number = 'REC' + str(registration_number + 1)
            data.append(registration_number)
            data.append(self.ui.fristName.text())
            data.append(self.ui.middleName.text())
            data.append(self.ui.lastName.text())
            date_of_birth = self.ui.dateOfBirth.date().toPyDate()
            data.append(date_of_birth.strftime("%d-%m-%Y"))
            if self.ui.radioFemale.isChecked():
                data.append('Female')
            if self.ui.radioMale.isChecked():
                data.append('Male')
            else:
                data.append('Other')
            data.append(self.ui.bloodGroup.currentText())
            data.append(self.ui.mobileNumber.text())
            data.append(self.ui.landLineNumber.text())
            data.append(self.ui.email.text())
            data.append(self.ui.permanantAddress.toPlainText())
            data.append(self.ui.addCity.text())
            data.append(self.ui.addState.currentText())
            data.append(self.ui.addDistrict.text())
            data.append(self.ui.addPincode.text())
            data.append(self.ui.patientDisease.text())
            data.append(self.ui.doctorName.text())
            data.append(self.ui.doctorRegistration.text())
            data.append(self.ui.illnessStage.currentText())
            data.append(self.ui.patientPriority.currentText())
            data.append(self.ui.transplantOrgan.currentText())
            query = """INSERT INTO receiver(registrationNumber , firstName ,middleName , lastName ,
                        dateOfBirth , gender , bloodGroup , mobileNumber , landLineNumber , email ,
                        address , city , district , state, pinCode, disease, doctorName, doctorRegistration,illnessStage,
                        priority, transplantingOrgan) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""
            self.cursor.execute(query, data)
            self.connection.commit()
            response = add_sucess()
            if response:
                self.renew_application()

    def change_form(self):
        self.ui.changeFormStack.setCurrentIndex(self.ui.formSelecter.currentIndex())

    def add_login_id(self, registration):
        pass

    def populate_record(self):
        try:
            donor_query = """select * from donor;"""
            self.cursor.execute(donor_query)
            donor_table = self.cursor.fetchall()
            required_rows = len(donor_table)
            self.ui.adminLoginStackDonorTable.setRowCount(required_rows)
            x = -1
            for i in donor_table:
                x = x + 1
                for j in range(0, 17):
                    self.ui.adminLoginStackDonorTable.setItem(x, j, QtWidgets.QTableWidgetItem(i[j]))

            receiver_query = """select * from receiver;"""
            self.cursor.execute(receiver_query)
            receiver_table = self.cursor.fetchall()
            required_rows = len(receiver_table)
            self.ui.adminLoginStackReceiverTable.setRowCount(required_rows)
            x = -1
            for i in receiver_table:
                x = x + 1
                for j in range(0, 21):
                    self.ui.adminLoginStackReceiverTable.setItem(x, j, QtWidgets.QTableWidgetItem(i[j]))
        except Exception as e:
            print(e)

    def populate_receiver(self, user_id):
        try:
            query = """select registrationNumber,priority,bloodGroup,doctorName from receiver;"""
            self.cursor.execute(query)
            waiting_table = self.cursor.fetchall()
            required_rows = len(waiting_table)
            self.ui.receiverLoginStackTable.setRowCount(required_rows)
            x = -1
            for i in waiting_table:
                x = x + 1
                for j in range(0, 5):
                    self.ui.receiverLoginStackTable.setItem(x, j, QtWidgets.QTableWidgetItem(i[j]))
        except Exception as e:
            print(e)

    def renew_application(self):
        self.ui.fristName.clear()
        self.ui.middleName.clear()
        self.ui.lastName.clear()
        self.ui.bloodGroup.clear()
        self.ui.mobileNumber.clear()
        self.ui.landLineNumber.clear()
        self.ui.email.clear()
        self.ui.permanantAddress.clear()
        self.ui.addCity.clear()
        self.ui.addState.clear()
        self.ui.addDistrict.setCurrentIndex(0)
        self.ui.addPincode.clear()
        self.ui.patientDisease.clear()
        self.ui.doctorName.clear()
        self.ui.doctorRegistration.clear()
        self.ui.donateBody.setChecked(False)
        self.ui.donateEyes.setChecked(False)
        self.ui.donateKidney.setChecked(False)
        self.ui.donatePancreas.setChecked(False)
        self.ui.donateHeart.setChecked(False)
        self.ui.donateLungs.setChecked(False)
        self.ui.illnessStage.setCurrentIndex(0)
        self.ui.patientPriority.setCurrentIndex(0)
        self.ui.transplantOrgan.setCurrentIndex(0)

    def admin_populate(self):
        try:
            if self.ui.adminRecordText.text() == '':
                raise Exception("blackRecord")
            else:
                record = self.ui.adminRecordText.text()
                if 'DON' in record:
                    query = """SELECT firstName, middleName, lastName, mobileNumber, dateOfBirth, gender, email 
                    FROM donor WHERE registrationNumber = ?;"""
                    if query is None:
                        raise Exception("User Does not exists")
                elif 'REC' in record:
                    query = """SELECT firstName, middleName, lastName, mobileNumber, dateOfBirth, gender, email, 
                    priority FROM receiver WHERE registrationNumber = ?;"""
                    if query is None:
                        raise Exception("User Does not exists")
                else:
                    raise Exception("Invalid Record ID type")
                self.cursor.execute(query, (record,))
                data = self.cursor.fetchall()
                data = list(data)
        except Exception as e:
            print(e)

    def __del__(self):
        self.connection.commit()
        self.connection.close()


class add_sucess(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'ODMS'
        self.left = 300
        self.top = 300
        self.width = 320
        self.height = 200
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        buttonReply = QtWidgets.QMessageBox.question(self, 'Registered Successfully', "Want to register another?",
                                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            return True
        else:
            return False


def password_reset():
    test = forgot()


def delete_record():
    test1 = noise()


def update_record():
    pass


class noise(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(noise, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle("Delete Record")
        self.setGeometry(300, 300, 300, 200)
        self.l1 = QtWidgets.QLabel("Confirm delete Record")
        self.l2 = QtWidgets.QLabel("State reason to delete Record")
        layout.addWidget(self.l1)
        layout.addWidget(self.l2)
        self.setLayout(layout)
        self.show()

    def btnstate(self):
        pass


class forgot(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(forgot, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle("Forgot Password")
        self.setGeometry(100, 100, 100, 100)
        self.b1 = QtWidgets.QPushButton("OK")
        self.b1.setCheckable(True)
        self.b1.toggle()
        self.b1.clicked.connect(lambda: self.whichbtn(self.b1))
        self.b1.clicked.connect(self.btnstate)
        self.l1 = QtWidgets.QLabel("Enter your First Name")
        self.l2 = QtWidgets.QLabel("Enter your Mobile Number")
        self.le1 = QtWidgets.QLineEdit()
        self.le2 = QtWidgets.QLineEdit()
        layout.addWidget(self.l1)
        layout.addWidget(self.le1)
        layout.addWidget(self.l2)
        layout.addWidget(self.le2)
        layout.addWidget(self.b1)
        self.userlabel = QtWidgets.QLabel("UserName:")
        self.password = QtWidgets.QLabel("Password")
        self.value1 = QtWidgets.QLabel()
        self.value2 = QtWidgets.QLabel()
        self.value1.setText(verif[0])
        self.value2.setText(verif[1])
        layout.addWidget(self.userlabel)
        layout.addWidget(self.value1)
        layout.addWidget(self.password)
        layout.addWidget(self.value2)
        self.setLayout(layout)
        self.show()

    def verify(self, fname, number):
        connection = sqlite3.connect('organRecord.db')
        cursor = connection.cursor()
        query = """SELECT loginId.userName,loginId.password FROM loginId INNER JOIN donor        
                ON loginId.userName=donor.registrationNumber
                WHERE donor.firstName=? and donor.mobileNumber = ?;"""
        cursor.execute(query, (fname, number))
        return cursor.fetchall()

    def btnstate(self):
        ant = self.verify(fname, number)
        if ant is not none:

    def whichbtn(self,x):
        pass

app = QtWidgets.QApplication(sys.argv)
win = Test()
sys.exit(app.exec_())
