
import flask
from flask import Flask, request, jsonify
import psycopg2
import os
import io
import random
from flask import Response, render_template
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

DATABASE = "my_db"
USER = "postgres"
PASSWORD = "sarOtah"
HOST = "127.0.0.1"
PORT = "5432"

ORGAN_FOLDER = os.path.join('static', 'organ_images')

app = Flask(__name__, template_folder='templates')
app.config['ORGAN_FOLDER'] = ORGAN_FOLDER
app.config["DEBUG"] = True


def dict_factory(cursor, row):
    d = {'result':[]}
    for r in row:
        row_dic = {}
        for idx, col in enumerate(cursor.description):
           row_dic[col[0]] = r[idx]
        d['result'].append(row_dic)
    return d

def table_factory(cursor, row):
    d = []
    colms = [desc[0] for desc in cursor.description]
    d.append ('   '.join((str(x) for x in colms)))
    for r in row:
        d.append('   '.join((str(x) for x in r)))
    return d

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Patient Portal</h1>
<p>A prototype API for working with database</p>'''


@app.route('/all', methods=['GET'])
def api_all():
    conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
    # 
    cur = conn.cursor()
    cur.execute('SELECT * FROM PATIENT')
    colms = [desc[0] for desc in cur.description]
    all_patients = cur.fetchall()
    # all_patients = dict_factory(cur, all_patients)
    # all_patients = table_factory(cur, all_patients)
    # return jsonify(all_patients)
    return render_template('table_overview.html',
                            title='Patient List',
                            column_names = colms,
                            rows=all_patients)


@app.route('/id', methods=['GET'])
def api_patientids():
    query_parameters = request.args
    patientid = query_parameters.get('patientid')
    conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
    cur = conn.cursor()

    # query = "SELECT * FROM PATIENT WHERE patientid=2"
    # query = "SELECT * FROM PATIENT WHERE patientid=%s"%patientid
    query = "SELECT * FROM PATIENT WHERE patientid=%s"
    cur.execute(query, [patientid])
    all_patients = cur.fetchall()
    all_patients = dict_factory(cur, all_patients)
    # all_patients = table_factory(cur, all_patients)
    return jsonify(all_patients)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/patients', methods=['GET'])
def api_filter():
    query_parameters = request.args

    patientid = query_parameters.get('patientid')
    age = query_parameters.get('age')
    weight = query_parameters.get('weight')
    treatment = query_parameters.get('treatment')


    query = "SELECT * FROM PATIENT WHERE"
    to_filter = []

    if patientid:
        query += ' patientid=%s AND'
        to_filter.append(patientid)
    if age:
        query += ' age=%s AND'
        to_filter.append(age)
    if weight:
        query += ' weight=%s AND'
        to_filter.append(weight)
    if treatment:
        query += ' treatment=%s AND'
        to_filter.append(treatment)
    # if not (patientid and published and weight and treatment):
    #     return page_not_found(404)

    query = query[:-4] + ';'
    conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
    cur = conn.cursor()

    cur.execute(query, to_filter)
    results = cur.fetchall()

    results = dict_factory(cur, results)
    # results = table_factory(cur, results)

    return jsonify(results)


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig


@app.route('/index', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.upper()
    return render_template('plot.html', forward_message=processed_text);


@app.route("/forward", methods=['POST'])
def move_forward():
    #Moving forward code
    forward_message = "Moving Forward..."
    return render_template('plot.html', forward_message=forward_message);

app.run()