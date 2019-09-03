import datetime
import re
import sqlite3
import sys

from PyQt5 import QtWidgets, uic


class Test:
    def __init__(self):
        self.ui = uic.loadUi('organ.ui')
        self.ui.show()
        self.create_database()
        self.ui.mainTab.setCurrentIndex(0)
        self.ui.loginButton.clicked.connect(self.login)
        self.ui.homeTabRegisterButton.clicked.connect(self.tabchange)
        self.ui.changeFormStack.setCurrentIndex(self.ui.formSelecter.currentIndex())
        self.ui.registerTabRegisterButton.clicked.connect(self.addRecord)

    def login(self):
        global user_name
        global password
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
            self.cursor.execute('select * from login_id where usr_name = ? and password = ?;',
                                ((user_name), (password)))
            chk = self.cursor.fetchall()
            if chk:
                self.ui.statusbar.showMessage("Login Successful")
            else:
                self.ui.statusNameLabel.setText('Incorrect Username or Password')

    def create_database(self):
        try:
            self.connection = sqlite3.connect('organRecord.db')
            self.cursor = self.connection.cursor()
            self.createdata()
            self.ui.statusbar.showMessage("Connected to Database")
        except Exception as e:
            print(e)
            self.ui.statusbar.showMessage(" Failed to Connect to Database:   Exiting Application")
            app.exit()

    def createdata(self):
        try:
            query = """CREATE TABLE IF NOT EXISTS donor(registrationNumber VARCHAR(5), firstName VARCHAR(20),
                    middleName VARCHAR(20), lastName VARCHAR(20), dateOfBirth DATE, gender VARCHAR(10), 
                    bloodGroup  VARCHAR(3), mobileNumber INTEGER, landLineNumber INTEGER, email VARCHAR(100),
                    address VARCHAR(255), city VARCHAR(30), district VARCHAR(30), state varchar(30), pinCode INTEGER, pledgeDate DATE,
                    donatingOrgans VARCHAR(100));"""
            self.cursor.execute(query)
            self.connection.commit()
            query = """CREATE TABLE IF NOT EXISTS receiver(registrationNumber VARCHAR(5), firstName VARCHAR(20),
                    middleName VARCHAR(20), lastName VARCHAR(20), dateOfBirth DATE, gender VARCHAR(10), 
                    bloodGroup  VARCHAR(3), mobileNumber INTEGER, landLineNumber INTEGER, email VARCHAR(100),
                    address VARCHAR(255), city VARCHAR(30), district VARCHAR(30),state varchar(30), pinCode INTEGER, disease VARCHAR(50),
                    doctorName VARCHAR(50), doctorRegistration VARCHAR(30), illnessStage VARCHAR(15), priority VARCHAR(20),
                    transplantingOrgan VARCHAR(10));"""
            self.cursor.execute(query)
            self.connection.commit()
            query = """CREATE TABLE loginId(userName varchar(10),password varchar(10))"""
            self.cursor.execute(query)
            query = """INSERT INTO loginId(userName, password)values('Admin','Admin@0'))"""
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(e)

    def tabchange(self):
        self.ui.mainTab.setCurrentIndex(1)

    def addRecord(self):
        if self.ui.formSelecter.currentIndex() == 0:
            data = []
            registration_number = 'DON1'
            self.cursor.execute("select registrationNumber from donor")
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
                donate = donate + '-Body'
            if self.ui.donateEyes.isChecked():
                donate = donate + '-Eyes'
            if self.ui.donateKidney.isChecked():
                donate = donate + '-Kidney'
            if self.ui.donatePancreas.isChecked():
                donate = donate + '-Pancreas'
            if self.ui.donateHeart.isChecked():
                donate = donate + '-Heart'
            if self.ui.donateLungs.isChecked():
                donate = donate + '-Lungs'
            data.append(donate)
            query = """INSERT INTO donor(registrationNumber , firstName ,middleName , lastName ,
                        dateOfBirth , gender , bloodGroup , mobileNumber , landLineNumber , email ,
                        address , city , district ,state, pinCode , pledgeDate ,donatingOrgans) 
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""
            self.cursor.execute(query, data)
            self.connection.commit()
            self.ui.statusbar.showMessage("Added Record")
        if self.ui.formSelecter.currentIndex() == 1:
            data = []
            registration_number = 'DON1'
            self.cursor.execute("select registrationNumber from receiver")
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
            data.append(self.ui.doctorRegistartion.text())
            data.append(self.ui.illnessStage.currentText())
            data.append(self.ui.patientPriority.currentText())
            data.append(self.ui.transplantOrgan.currentText())
            query = """INSERT INTO receiver(registrationNumber , firstName ,middleName , lastName ,
                        dateOfBirth , gender , bloodGroup , mobileNumber , landLineNumber , email ,
                        address , city , district , state, pinCode, disease, doctorName, doctorRegistration,illnessStage,
                        priority, transplantingOrgan) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""
            self.cursor.execute(query, data)
            self.connection.commit()

    def addloginid(self, registration):
        pass

    def __del__(self):
        self.connection.commit()
        self.connection.close()


app = QtWidgets.QApplication(sys.argv)
win = Test()
sys.exit(app.exec_())
