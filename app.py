from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session


app = Flask(__name__)
#app.secret_key = '#123%123'
app.config['SECRET_KEY'] = 'anystringthatyoulike'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Session(app)
db = SQLAlchemy(app)


#Creating database
class Parking(db.Model):
    plate = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(2), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)

class Slot(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    status = db.Column(db.Boolean)
    vehicle_type = db.Column(db.String(50))
    plate = db.Column(db.String(50))

#Drop and recreate the table to include the 'name' column
#with app.app_context():
    #db.drop_all()
    #db.create_all()


@app.route('/', methods=["GET", "POST"])
def index():

    num = None
    if request.method == "POST":
        number = request.form["number_plate"] #vno_entry
        
        number_found = db.session.query(Parking.query.filter_by(plate=number).exists()).scalar()

        if number_found:
            car = db.session.query(Parking).filter_by(plate=number).first()
            slot_number = db.session.query(Slot).filter_by(status=False).first()
            slot_number.status = True
            slot_number.vehicle_type = car.vehicle_type
            slot_number.plate = car.plate
            db.session.commit()
            allocated_slot_id = slot_number.id
            flash(f"Access Granted , slot : { slot_number.id }" if allocated_slot_id else "No vacant slots available")
        else:
            flash("Number not registered")
        
        return render_template('index.html')
    else:    
        return render_template('index.html')

@app.route("/exit", methods=["GET", "POST"])
def exit():
    if request.method == "POST":
        plate = request.form["number_plate"]
        number_found = db.session.query(Parking.query.filter_by(plate=plate).exists()).scalar()
        if number_found:
            flash("Exit")
            car = db.session.query(Slot).filter_by(plate=plate).first()
            car.status = False
            car.vehicle_type = None 
            car.plate = None
            db.session.commit()
        return redirect(url_for('index'))    
    
    return redirect(url_for('index')) 


@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":
        name = request.form["name"]
        plate = request.form["plate"]
        gender = request.form['gender']
        vehicle_type = request.form['vehicle_type']
       
        plate_exists = db.session.query(Parking.query.filter_by(plate=plate).exists()).scalar()

        if plate_exists:
            flash("Plate number already exists!")
        else:
            new_entry = Parking(plate = plate, name=name, gender=gender, vehicle_type=vehicle_type)
            db.session.add(new_entry)
            db.session.commit()
            flash("Registration successful!")
            return redirect(url_for('index'))
    
    return render_template("register.html")



if __name__ == "__main__":
    with app.app_context():
        db.create_all
    app.run(debug=True)