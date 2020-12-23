from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
import sqlite3
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['DEBUG'] = True
db = SQLAlchemy(app)

class Patient(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    First_Name = db.Column(db.String(20),nullable=False)
    Last_Name = db.Column(db.String(20), nullable=False)
    DOB = db.Column(db.String(12), nullable=False)
    Phone_Num = db.Column(db.String(30), nullable=False)
    Address = db.Column(db.String(40), nullable=True)
    Insurance_Tpye = db.Column(db.String(20),nullable=True)
    Medical_Number = db.Column(db.String(20),nullable=True)

    def __repr__(self):
        return str(self.id)

class Appointment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    Patient_Name = db.Column(db.String(30), nullable=False)
    Start_Date = db.Column(db.String(20), nullable=False)
    Start_Time = db.Column(db.String(20), nullable=False)
    Appointment_Type = db.Column(db.String(20), nullable=False)
    Patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))

    def __repr__(self):
        return "Appointment, " + str(self.id)


# Home Page
@app.route('/')
def index():
    posts = Patient.query.order_by(Patient.First_Name).all()
    return render_template('index.html', posts=posts)

# search bar
@app.route('/search')
def search():
    q = request.args.get('query')
    if q:
        posts = Patient.query.filter(Patient.Last_Name.contains(q) | Patient.First_Name.contains(q) ).order_by(Patient.First_Name).all()
    else:
        posts = Patient.query.all()
    return render_template('index.html', posts=posts)    

# create a new patient
@app.route('/new', methods=['GET','POST'])
def new():

    if request.method == 'POST':
        post_First_Name = request.form['Fname']
        post_Last_Name = request.form['Lname']
        post_DOB = request.form['DOB']
        post_Phone_num = request.form['Pnum']
        post_Address = request.form['Address']
        post_Insurance_Type = request.form['IT']
        post_Medi_Num = request.form['MN']
        new_patient = Patient(First_Name=post_First_Name, Last_Name=post_Last_Name, DOB=post_DOB, Phone_Num=post_Phone_num)
        db.session.add(new_patient)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('new.html')

# create a new appointment
@app.route('/appointment/<int:id>', methods=['GET','POST'])
def appointment(id):

    # here u neeed the post since is based off an id
    all_p = Patient.query.get_or_404(id)

    if request.method == 'POST':
        post_Patient_Full_Name = request.form['Pname']
        post_Start_Date = request.form['Sdate']
        post_Start_Time = request.form['Stime']
        post_Appointment_Type = request.form['AP']
        new_appointment = Appointment(Patient_Name=post_Patient_Full_Name, Start_Date=post_Start_Date, Start_Time=post_Start_Time, Appointment_Type=post_Appointment_Type, Patient_id=str(id))
        db.session.add(new_appointment)
        db.session.commit()
        return redirect('/profile/page/'+str(int(id)))
    else:
        return render_template('appointment.html', post=all_p)


# all profile
@app.route('/profile')
def profile():

    all_posts = Patient.query.all()
    return render_template('profile.html', posts=all_posts)

# certain profile
@app.route('/profile/page/<int:id>')
def page(id):
    # here we get the id of the patient
    curr = Patient.query.get_or_404(id)
    # here it gets the id based on realtionship
    # then is first order_by Start_Date then Start_Time
    # since we have an Patient_id in the database 
    # appointment = Appointment.query.filter_by(Patient_id=id).all()

    # Here we get the first and last name from patients database then we filter it within appointment database based on the first and last name
    F = curr.First_Name + " " + curr.Last_Name
    appointments = Appointment.query.filter(Appointment.Patient_Name.contains(str(F))).order_by(Appointment.Start_Date).order_by(Appointment.Start_Time).all()
    return render_template('page.html', post=curr, appointment=appointments)

# delete button for Patient
@app.route('/profile/delete/<int:id>')
def delete(id):
    curr = Patient.query.get_or_404(id)
    app = Appointment.query.filter_by(Patient_id=id).all()
    db.session.delete(curr)
    for a in app:
        db.session.delete(a) 
    db.session.commit()
    return redirect('/')

# edit button for Patient
@app.route('/profile/edit/<int:id>', methods=['GET','POST'])
def edit(id):

    post = Patient.query.get_or_404(id)

    if request.method == 'POST':
        post.First_Name = request.form['Fname']
        post.Last_Name = request.form['Lname']
        post.DOB = request.form['DOB']
        post.Phone_Num = request.form['Pnum']
        post.Address = request.form['Address']
        post.Insurance_Tpye = request.form['IT']
        post.Medical_Number = request.form['MN']
        db.session.commit()
        return redirect('/profile/page/'+str(int(id)))
    else:
        return render_template('edit.html',post=post)

# delete button for appointment
@app.route('/profile/page/delete_a/<int:id>')
def delete_appointment(id):
    curr = Appointment.query.get_or_404(id)

    F = curr.Patient_Name.split(' ')[0]
    # here since is "Justin Zhang" we just want Justin
    # here if F[0] is J instead of " 
    # this is just used to remove "" in the front
    # this is only used for redirect only
    if F[0].isalpha():
        F = curr.Patient_Name.split(' ')[0]
    else:
        F = curr.Patient_Name.split(' ')[0][1:]


    db.session.delete(curr)
    db.session.commit()
    # here get the patient since is in a list we have to do i[0]
    i = Patient.query.filter_by(First_Name=F).all()
    return redirect('/profile/page/'+str(i[0]))

# edit button for appointment
@app.route('/profile/page/edit_a/<int:id>', methods=['GET','POST'])
def edit_appointment(id):

    post = Appointment.query.get_or_404(id)\
    # here since is "Justin Zhang" we just want Justin
    F = post.Patient_Name.split(' ')[0]
    # here if F[0] is J instead of " 
    # this is just used to remove "" in the front
    # this is only used for redirect only
    if F[0].isalpha():
        F = post.Patient_Name.split(' ')[0]
    else:
        F = post.Patient_Name.split(' ')[0][1:]

    if request.method == 'POST':
        post.Patient_Full_Name = request.form['Pname']
        post.Start_Date = request.form['Sdate']
        post.Start_Time = request.form['Stime']
        post.Appointment_Type = request.form['AP']
        db.session.commit()

        #Here I got the number by using the id from patient __repr__
        # first i filter_by the name from appointment and find it with in Patient
        # then i just take the id assigned to that patient
        i = Patient.query.filter_by(First_Name=F).all()
        
        # here get the patient since is in a list we have to do i[0]
        return redirect('/profile/page/'+str(i[0]))
    else:
        return render_template('edit_a.html', post=post)


if __name__ == "__main__":
    app.run(debug=True)