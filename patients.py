# to import another python file just same folder and type the python file name
import app
import csv
import sqlite3

#connect to database
connection = sqlite3.connect("new.db")
cursor = connection.cursor()


# read file patients
with open('patients.csv', 'r') as file:
    for row in file:
        cursor.execute("INSERT INTO Patient (First_Name,Last_Name,DOB,Phone_Num) VALUES (?,?,?,?)", row.split(','))
        connection.commit()
connection.close()