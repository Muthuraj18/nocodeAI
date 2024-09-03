from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from flask import Blueprint, render_template

bp = Blueprint('app3', __name__, template_folder='templates', static_folder='static')

@bp.route('/')
def index():
    return render_template('index3.html')

app = Flask(__name__)

# Database connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '2004',
    'host': 'localhost',
    'port': '5432'  # Change this if your PostgreSQL server is using a different port
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        date = request.form['date']
        precipitation = request.form['precipitation']
        temp_max = request.form['temp_max']
        temp_min = request.form['temp_min']
        wind = request.form['wind']
        weather = request.form['weather']

        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Insert data into the database
        insert_query = "INSERT INTO weather_data (date, precipitation, temp_max, temp_min, wind, weather) " \
                       "VALUES (%s, %s, %s, %s, %s, %s)"
        data = (date, precipitation, temp_max, temp_min, wind, weather)
        cursor.execute(insert_query, data)

        conn.commit()
        conn.close()

        return redirect(url_for('result', date=date))

    return render_template('index3.html')

@app.route('/result/<date>')
def result(date):
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Fetch data from the database for the specified date
    select_query = "SELECT * FROM weather_data WHERE date = %s"
    cursor.execute(select_query, (date,))
    row = cursor.fetchone()

    conn.close()

    return render_template('result3.html', data=row)

if __name__ == '__main__':
    app.run(debug=True)
