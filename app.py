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
    priority = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)

class Slot(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    status = db.Column(db.Boolean)
    priority = db.Column(db.String(20))
    vehicle_type = db.Column(db.String(50))
    plate = db.Column(db.String(50))


#Drop and recreate the table when needed
#with app.app_context():
    #db.drop_all()
    #db.create_all()


@app.route('/', methods=["GET", "POST"])
def index():

    #for id in range(1, 100):
        #priority = "Staff"
        #status = False
        #entry_1 = Slot(id=id,status=status,priority=priority,vehicle_type=None,plate=None)
        #db.session.add(entry_1)
        #db.session.commit()

    #for id in range(101, 200):
        #priority = "Female"
        #status = False
        #entry_2 = Slot(id=id,status=status,priority=priority,vehicle_type=None,plate=None)
        #db.session.add(entry_2)
        #db.session.commit()

    #for id in range(201, 300):
        #priority = "Male"
        #status = False
        #entry_3 = Slot(id=id,status=status,priority=priority,vehicle_type=None,plate=None)
        #db.session.add(entry_3)
        #db.session.commit()

    num = None
    if request.method == "POST":
        number = request.form["number_plate"] #vno_entry
        Staff = "Staff"
        Male = "Male"
        Female = "Female"
        number_found = db.session.query(Parking.query.filter_by(plate=number).exists()).scalar()
        

        Entry = db.session.query(Parking).filter_by(plate=number).first()
        priority_val = Entry.priority
        
        
        if number_found:
            car = db.session.query(Parking).filter_by(plate=number).first()
            slot_number = db.session.query(Slot).filter_by(status=False).filter_by(priority=priority_val).first()
            slot_number.status = True
            slot_number.vehicle_type = car.vehicle_type
            slot_number.plate = car.plate
            db.session.commit()
            allocated_slot_id = slot_number.id
            flash(f"Access Granted , Go to { slot_number.priority } Parking slot : { slot_number.id }" if allocated_slot_id else "No vacant slots available")
        else:
            flash("Number not registered")
        
        return render_template('index.html')
    else:   
    
        return render_template('index.html')

@app.route("/display" , methods=["GET" , "POST"])
def display():
    data = db.session.query(Slot).all()
    return render_template("Dashboard.html" , data=data)

@app.route("/exit", methods=["GET", "POST"])
def exit():
    if request.method == "POST":
        plate = request.form["number_plate"]
        number_found = db.session.query(Slot.query.filter_by(plate=plate).exists()).scalar()
        if number_found:
            flash("Exit")
            car = db.session.query(Slot).filter_by(plate=plate).first()
            car.status = False
            car.vehicle_type = None 
            car.plate = None
            db.session.commit()
        else:
            flash("Car was not registered during entry")
        return redirect(url_for('index'))    
    
    return redirect(url_for('index')) 


@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":
        name = request.form["name"]
        plate = request.form["plate"]
        priority = request.form["priority"]
        vehicle_type = request.form['vehicle_type']
       
        plate_exists = db.session.query(Parking.query.filter_by(plate=plate).exists()).scalar()

        if plate_exists:
            flash("Plate number already exists!")
        else:
            new_entry = Parking(plate = plate, name=name, priority=priority, vehicle_type=vehicle_type)
            db.session.add(new_entry)
            db.session.commit()
            flash("Registration successful!")
            return redirect(url_for('index'))
    
    return render_template("register.html")



if __name__ == "__main__":
    with app.app_context():
        db.create_all
    app.run(debug=True)