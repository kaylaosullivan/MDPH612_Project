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

DATABASE = "db612"
USER = "postgres"
PASSWORD = "1202db"
HOST = "127.0.0.1"
PORT = "5432"

ORGAN_FOLDER = os.path.join('static')

app = Flask(__name__, template_folder='templates')
app.secret_key = 'women4communism'

app.config['ORGAN_FOLDER'] = ORGAN_FOLDER
app.config["DEBUG"] = True

@app.route('/')
def start():
    return redirect('http://127.0.0.1:5000/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        p_name = request.form['username']
        password = request.form['password']

        query_patient = """SELECT PATIENT.PATIENTID, PATIENT.NAME, PATIENT.PASSWORD FROM PATIENT"""
        
        conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        cur = conn.cursor()
        cur.execute(query_patient)
        results_patient =cur.fetchall()
        print(results_patient)

        print(results_patient[:][1])
        print(results_patient[:][2])

        for i in range(len(results_patient)):
            if p_name == results_patient[i][1] and password == results_patient[i][2]:
                session['p_id'] = i+1
                session['p_name'] = p_name 
                error = None
                return redirect('http://127.0.0.1:5000/reminder')

            if p_name == results_patient[i][1] and not password == results_patient[i][2]:
                error = 'Invalid Password. Please try again.'
                print("error 1")
                break
            else:
                error = 'The name you entered does not exist. Please try again.'
                print("error 2")

    return render_template('login.html', error=error)


@app.route('/reminder', methods=['GET', 'POST'])
def warning():
    return render_template('reminder.html')




# @app.route('/home', methods=['GET'])
# def show_list():
#     p_id =  session.get('p_id', None)
#     full_filename = os.path.join(app.config['ORGAN_FOLDER'], 'test.png')
#     return render_template("organs.html", user_image = full_filename, p_id = p_id)

@app.route('/home',  methods=['GET', 'POST'])
def load_patient():
    # p_id = request.form['p_id']
    # session['p_id'] = p_id
    p_id = session.get('p_id', None)


    if p_id != "": 
        query_img = """SELECT IMAGE.IMAGEID, IMAGE.NAME, IMAGE.FULLPATH FROM IMAGE 
            INNER JOIN PATIENT_IMAGE ON IMAGE.IMAGEID=PATIENT_IMAGE.IMAGEID 
            WHERE PATIENT_IMAGE.PATIENTID=%s"""%(p_id)
        query_organ =  """SELECT ORGAN.ORGANID, ORGAN.NAME, ORGAN.COLOUR, ORGAN.DESCRIPTION FROM ORGAN 
            INNER JOIN PATIENT_ORGAN ON ORGAN.ORGANID=PATIENT_ORGAN.ORGANID 
            WHERE PATIENT_ORGAN.PATIENTID=%s"""%(p_id)
        query_name = """SELECT PATIENT.NAME FROM PATIENT 
            WHERE PATIENT.PATIENTID=%s"""%(p_id)

        conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        cur = conn.cursor()
        cur.execute(query_img)
        results_img = cur.fetchall()

        cur.execute(query_organ)
        results_organ = cur.fetchall()

        cur.execute(query_name)
        p_name = cur.fetchall()[0][0]
        print(p_name)

    else:
        results_organ = []
        results_img = []
        p_name=""

    checked = 'showContours' in request.form
    print(checked)

    print(results_img)
    print(results_organ)

    if (checked):
        select_image = results_img[1][2]
    else:
        select_image = results_img[0][2]
    full_filename = os.path.join(app.config['ORGAN_FOLDER'], select_image)

    print(full_filename)
    session['image_path'] = os.path.join(app.config['ORGAN_FOLDER'], results_img[1][2])


    if ('organ_butt' in request.form):
        organ_selected = request.form['organ_butt']
    else:
        organ_selected=""
    print(organ_selected)

 
    return render_template("organs.html", user_image = full_filename
                                        , rows_img = results_img,
                                        rows_org = results_organ,
                                        p_id = p_id,
                                        p_name = p_name,
                                        select_image = select_image,
                                        is_checked = checked
                                        )
    


@app.route('/info', methods=['POST'])
def load_info():

    p_id = session.get('p_id', None)
    o_id = request.form["organ_butt"]
    
    
    if p_id != "": 
        # query_img = """SELECT IMAGE.IMAGEID, IMAGE.NAME, IMAGE.FULLPATH FROM IMAGE 
        #     INNER JOIN PATIENT_IMAGE ON IMAGE.IMAGEID=PATIENT_IMAGE.IMAGEID 
        #     WHERE PATIENT_IMAGE.PATIENTID=%s"""%(p_id)
        query_organ =  """SELECT ORGAN.ORGANID, ORGAN.NAME, ORGAN.COLOUR, ORGAN.DESCRIPTION FROM ORGAN 
            WHERE ORGAN.ORGANID=%s"""%(o_id)
        # query_name = """SELECT PATIENT.NAME FROM PATIENT 
        #     WHERE PATIENT.PATIENTID=%s"""%(p_id)

        conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        cur = conn.cursor()
        # cur.execute(query_img)
        # colms = [desc[0] for desc in cur.description]
        # results_img = cur.fetchall()

        cur.execute(query_organ)
        results_organ = cur.fetchall()


    else:
        results_organ = []
    
    print(results_organ)

    #full_filename = session.get('image_path', None)
    
    org_file = "p"+str(p_id)+"_images/"+results_organ[0][1]+".png"
    full_filename = os.path.join(app.config['ORGAN_FOLDER'], org_file)

    print(full_filename)
    return render_template("info.html", user_image = full_filename,
                                        rows_org = results_organ,
                                        p_id = p_id
                                        )
    

    


# @app.route('/plot.png')
# def plot_png():
#     fig = create_figure()
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')

# def create_figure():
#     fig = Figure()
#     axis = fig.add_subplot(1, 1, 1)
#     xs = np.arange(100)
#     ys = np.sin(xs/10) 
#     axis.plot(xs, ys)
#     return fig


	

# @app.route('/plot', methods=['POST', 'GET'])
# def show_plot():
#     return render_template("plot.html")

app.run()




