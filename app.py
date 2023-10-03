from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.utils import secure_filename

#TEMP
import io
import cv2
from matplotlib import pyplot as plt
import numpy as np
import imutils
import easyocr
import os
import uuid


app = Flask(__name__)
#app.secret_key = '#123%123'
app.config['SECRET_KEY'] = 'anystringthatyoulike'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Session(app)
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
'''
@app.route("/check", methods=["GET" , "POST"])
def check():
    if request.method == "POST":
    
    # Read the uploaded image
        #uploaded_file = request.files['file']
        #if uploaded_file.filename != '':
           # image_path = secure_filename(uploaded_file.filename)
           # uploaded_file.save(image_path)
        #else:
            #flash('No file uploaded')
            #return redirect(request.url)
    

        # Image processing
        
            return render_template("index.html", result=text)
        else:
            flash("Number plate not detected")
            return redirect(request.url)
    else:
        flash("WORKING")
        return render_template("check.html")
'''


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')

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

    # num = None
    # if request.method == "POST":
    #     if 'file-input' not in request.files:
    #         flash("NO FILE UPLOADED")
    #     uploaded_file = request.files.get("file-input")
    #     print(uploaded_file.filename)
    #     uploaded_file.save('img.png')
    #     filename = secure_filename(uploaded_file.filename)
    #     print(app.config['UPLOAD_FOLDER'] + filename)
    #     uploaded_file.save(app.config['UPLOAD_FOLDER'] + filename)
    #     '''if not os.path.exists(app.config['UPLOAD_FOLDER']):
    #         os.makedirs(app.config['UPLOAD_FOLDER'])

    #     # Generate a unique filename using uuid
    #     unique_filename = str(uuid.uuid4()) + '.jpg'

    #     # Save the uploaded image with the unique filename
    #     uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))'''
        
        
    #     image_path = None
    #     #if uploaded_file.filename != '':
        #image_path = secure_filename(uploaded_file.filename)
        #uploaded_file.save(image_path)
        


        #if image_path is None:
            #flash("image path none")
            #return render_template("index.html")

        
        
        
        
def process_image():
    img = cv2.imread("uploads/uploaded_image.png")
    #img = cv2.imdecode(np.fromfile(image_path, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(bfilter, 30, 200)

    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(keypoints)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    location = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 10, True)
        if len(approx) == 4:
            location = approx
            break

    if location is not None:
        mask = np.zeros(gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [location], 0, 255, -1)
        new_image = cv2.bitwise_and(img, img, mask=mask)

        (x, y) = np.where(mask == 255)
        (x1, y1) = (np.min(x), np.min(y))
        (x2, y2) = (np.max(x), np.max(y))
        cropped_number_plate = gray[x1:x2 + 1, y1:y2 + 1]

        # Perform OCR on the cropped number plate
        reader = easyocr.Reader(['en'])
        result = reader.readtext(cropped_number_plate)

        if result:
            text = result[0][-2]
            #flash(result)
        else:
            text = "No text found in the cropped number plate"

    #number = request.form["number_plate"] #vno_entry
    number = text
    
    #Check what value a particular registeration in giving
    #return render_template("index.html", text=text)

    number_found = db.session.query(Parking.query.filter_by(plate=number).exists()).scalar()     
    if number_found:
        Entry = db.session.query(Parking).filter_by(plate=number).first()
        priority_val = Entry.priority
        car = db.session.query(Parking).filter_by(plate=number).first()
        slot_number = db.session.query(Slot).filter_by(status=False).filter_by(priority=priority_val).first()
        slot_number.status = True
        slot_number.vehicle_type = car.vehicle_type
        slot_number.plate = car.plate
        db.session.commit()
        allocated_slot_id = slot_number.id
        return f"Access Granted , Go to { slot_number.priority } Parking slot : { slot_number.id }" if allocated_slot_id else "No vacant slots available"
    else:
        
        return text


@app.route("/display" , methods=["GET" , "POST"])
def display():
    data = db.session.query(Slot).all()
    return render_template("Dashboard.html" , data=data)

@app.route('/test' , methods =["GET" ,"POST"])
def test():
    return render_template("tess.html")

@app.route('/upload', methods=["POST"])
def upload():
    try:
        octet_stream_data = request.get_data()

        image_format = "png"  # Change this based on your data

        image_data = io.BytesIO(octet_stream_data)

        filename = "uploads/uploaded_image.{}".format(image_format)
        with open(filename, 'wb') as f:
            f.write(image_data.getvalue())
        
        response = process_image()
        return response,200
        
        return "Image saved successfully!"
    except Exception as e:
        return str(e), 400

@app.route("/exit", methods=["GET", "POST"])
def exit():
    if request.method == "POST":
        #plate = request.form["number_plate"]

        img = cv2.imread('image5.jpg')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(bfilter, 30, 200)

        keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(keypoints)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        location = None
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 10, True)
            if len(approx) == 4:
                location = approx
                break

        if location is not None:
            mask = np.zeros(gray.shape, np.uint8)
            new_image = cv2.drawContours(mask, [location], 0, 255, -1)
            new_image = cv2.bitwise_and(img, img, mask=mask)

            (x, y) = np.where(mask == 255)
            (x1, y1) = (np.min(x), np.min(y))
            (x2, y2) = (np.max(x), np.max(y))
            cropped_number_plate = gray[x1:x2 + 1, y1:y2 + 1]

            # Perform OCR on the cropped number plate
            reader = easyocr.Reader(['en'])
            result = reader.readtext(cropped_number_plate)

            if result:
                text = result[0][-2]
                #flash(result)
            else:
                text = "No text found in the cropped number plate"
        plate = text

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