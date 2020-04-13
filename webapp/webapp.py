from flask import Flask, render_template
from flask import  request, Response, session, redirect, url_for
import psycopg2
import os
import io
import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# Database Information
DATABASE = "db612"
USER = "postgres"
PASSWORD = "1202db"
HOST = "127.0.0.1"
PORT = "5432"

# Configure Folders/Flask
ORGAN_FOLDER = os.path.join('static')

app = Flask(__name__, template_folder='templates')
app.secret_key = 'women4communism'

app.config['ORGAN_FOLDER'] = ORGAN_FOLDER
app.config["DEBUG"] = True


# Redirect root page to login
@app.route('/')
def start():
    return redirect('http://127.0.0.1:5000/login')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    
    if request.method == 'POST':
        # Get username and password input by user
        p_name = request.form['username']
        password = request.form['password']

        # Query all patients from database
        query_patient = """SELECT PATIENT.PATIENTID, PATIENT.NAME, PATIENT.PASSWORD FROM PATIENT"""
        
        conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        cur = conn.cursor()
        cur.execute(query_patient)
        results_patient =cur.fetchall()

        # See if name exists in database and if password matches
        for i in range(len(results_patient)):
            # Both name and password match, redirect to reminder page
            if p_name == results_patient[i][1] and password == results_patient[i][2]:
                # Save patient id and name as session variables
                session['p_id'] = i+1
                session['p_name'] = p_name 
                error = None
                return redirect('http://127.0.0.1:5000/reminder')

            # Name exists but wrong password
            if p_name == results_patient[i][1] and not password == results_patient[i][2]:
                error = 'Invalid Password. Please try again.'
                break

            # Name doesn't exist in file
            else:
                error = 'The name you entered does not exist. Please try again.'

    return render_template('login.html', error=error)


# Load reminder page
@app.route('/reminder', methods=['GET', 'POST'])
def warning():
    return render_template('reminder.html')


# Load main home page
@app.route('/home',  methods=['GET', 'POST'])
def load_patient():
    # get current user's patientID and name
    p_id = session.get('p_id', None)
    p_name = session.get('p_name', None)

    # Retrieve patient images and organs from database
    if p_id != "": 
        query_img = """SELECT IMAGE.IMAGEID, IMAGE.NAME, IMAGE.FULLPATH FROM IMAGE 
            INNER JOIN PATIENT_IMAGE ON IMAGE.IMAGEID=PATIENT_IMAGE.IMAGEID 
            WHERE PATIENT_IMAGE.PATIENTID=%s"""%(p_id)
        query_organ =  """SELECT ORGAN.ORGANID, ORGAN.NAME, ORGAN.COLOUR, ORGAN.DESCRIPTION FROM ORGAN 
            INNER JOIN PATIENT_ORGAN ON ORGAN.ORGANID=PATIENT_ORGAN.ORGANID 
            WHERE PATIENT_ORGAN.PATIENTID=%s"""%(p_id)
        # query_name = """SELECT PATIENT.NAME FROM PATIENT 
        #     WHERE PATIENT.PATIENTID=%s"""%(p_id)

        conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        cur = conn.cursor()
        cur.execute(query_img)
        results_img = cur.fetchall()

        cur.execute(query_organ)
        results_organ = cur.fetchall()

        #cur.execute(query_name)
        # p_name = cur.fetchall()[0][0]

    else:
        results_organ = []
        results_img = []
        # p_name=""

    # See if "show outlined organs" checkbox is checked
    checked = 'showContours' in request.form

    if (checked):
        select_image = results_img[1][2]  # Image with contours
    else:
        select_image = results_img[0][2]  # Image without contours
    
    # File name of selected image
    full_filename = os.path.join(app.config['ORGAN_FOLDER'], select_image)
    session['image_path'] = os.path.join(app.config['ORGAN_FOLDER'], results_img[1][2])
 
    return render_template("organs.html", user_image = full_filename
                                        , rows_img = results_img,
                                        rows_org = results_organ,
                                        p_id = p_id,
                                        p_name = p_name,
                                        select_image = select_image,
                                        is_checked = checked
                                        )
    

# Load organ info page
@app.route('/info', methods=['GET','POST'])
def load_info():
    p_id = session.get('p_id', None)   # Current user's ID
    o_id = request.form["organ_butt"]  # Get organ button selected
    
    # Retrieve organ information from database
    if p_id != "": 
        query_organ =  """SELECT ORGAN.ORGANID, ORGAN.NAME, ORGAN.COLOUR, ORGAN.DESCRIPTION FROM ORGAN 
            WHERE ORGAN.ORGANID=%s"""%(o_id)

        conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        cur = conn.cursor()
        cur.execute(query_organ)
        results_organ = cur.fetchall()

    else:
        results_organ = []
    

    # to display contoured image
    #full_filename = session.get('image_path', None)
    
    # Display image with selected organ contoured (file saved as p{p_id}_images/{Organ Name}.png)
    org_file = "p"+str(p_id)+"_images/"+results_organ[0][1]+".png"
    full_filename = os.path.join(app.config['ORGAN_FOLDER'], org_file)

    return render_template("info.html", user_image = full_filename,
                                        rows_org = results_organ,
                                        p_id = p_id
                                        )

app.run()




