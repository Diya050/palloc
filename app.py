from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import cv2
import numpy as np

app = Flask(__name__)
app.secret_key = "APEX"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Parking.db'  # SQLite database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Parking(db.Model):
    __tablename__ = 'parking'
    plate = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(100))
    v_type = db.Column(db.Integer)

    def __init__(self, name, plate, gender, v_type):
        self.name = name
        self.plate = plate
        self.gender = gender
        self.v_type = v_type

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    
    if request.method == "POST":
        name = request.form.get("name")
        plate = request.form.get("plate")
        gender = request.form.get("gender") 
        v_type = request.form.get("vehicle")       

        found_plate = Parking.query.filter_by(plate=plate).first()
        if found_plate:
            flash("Already Registered")
            #Display message already registered
        else:
            plate_number = Parking(plate , "")
            db.session.add(plate_number)
            db.commit()
            
            flash("Registered")
    
    return redirect(url_for(register))

@app.route('/detect', methods=['POST'])
def detect():
    if request.method == "POST":
        plate = request.form.get("plate")
        parking_record = Parking.query.filter_by(plate=plate).first()
        if parking_record:
            session["plate"] = parking_record.plate
            return render_template("found.html", record=parking_record)
        else:
            return render_template("not_found.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
