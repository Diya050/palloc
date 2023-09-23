from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secretkey'

db = SQLAlchemy(app)

class Parking(db.Model):
    plate = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(2), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)

#Drop and recreate the table to include the 'name' column
with app.app_context():
    db.drop_all()
    db.create_all()

@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":
        name = request.form["name"]
        plate = request.form["plate"]
        gender = request.form['gender']
        vehicle_type = request.form['vehicle_type']
       
        plate_exists = db.session.query(Parking.query.filter_by(plate=plate).exists()).scalar()

        if plate_exists:
            flash('Plate number already exists!', 'danger')
        else:
            new_entry = Parking(plate = plate, name=name, gender=gender, vehicle_type=vehicle_type)
            db.session.add(new_entry)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))
    
    return render_template("register.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all
    app.run(debug=True)
