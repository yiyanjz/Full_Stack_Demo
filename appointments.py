# to import another python file just same folder and type the python file name
import app
import csv
import sqlite3

#connect to database
connection = sqlite3.connect("new.db")
cursor = connection.cursor()

# read file appointment
with open('appointments.csv', 'r') as file:
    for row in file:
        cursor.execute("INSERT INTO Appointment (Patient_Name,Start_Date,Start_Time,Appointment_Type) VALUES (?,?,?,?)", row.split(','))
        connection.commit()
connection.close()