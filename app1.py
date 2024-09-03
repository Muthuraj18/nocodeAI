import calendar
from flask import Flask, jsonify, render_template, request
import psycopg2
from sklearn.calibration import LabelEncoder
from transformers import T5Tokenizer, T5ForConditionalGeneration
from datetime import datetime
import dateparser
import spacy
from flask import Blueprint, render_template

bp = Blueprint('app1', __name__, template_folder='templates', static_folder='static')

@bp.route('/')
def index():
    return render_template('index1.html')

app = Flask(__name__)

# PostgreSQL configuration
db_host = 'localhost'
db_name = 'postgres'
db_user = 'postgres'
db_password = '2004'

# Load the spaCy model (English)
nlp = spacy.load("en_core_web_sm")

# Replace "path/to/t5_model" with the actual path to your locally saved model folder
model_path = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)

column_mapping = {
    "Date": "date",
    "Precipitation": "precipitation",
    "MAX Temperature": "temp_max",
    "MIN Temperature": "temp_min",
    "Wind": "wind",
    "Weather": "weather"
}

def convert_date_format(date_str):
     print('\n\n parameter',date_str)
     date_obj = dateparser.parse(str(date_str))
     print('oubtside of the if condion',date_obj)
     if date_obj:
         formatted_date = date_obj.strftime('%d-%m-%Y')
         print('inside of the if condion',formatted_date)
         return formatted_date
     else:
         return "Invalid date format"

def format_date(date_str):
    # Convert the date to "DD-MM-YYYY" format
    formatted_date = convert_date_format(date_str)
    return formatted_date

def extract_and_format_dates(text):
    doc = nlp(text)
    print('\n\nin funcation',doc)
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    print('\n\nin funcation',dates)
    # formatted_dates = [format_date(date_str) for date_str in dates]
    print('\n\nin funcation',dates)
    return dates

def get_sql(query):
    input_text = "translate English to SQL: %s </s>" % query
    inputs = tokenizer.encode(input_text, return_tensors="pt")

    outputs = model.generate(inputs)
    generated_sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    generated_sql_query = generated_sql_query.replace("table", "weather_data")
    
    for word in column_mapping.keys():
        generated_sql_query = generated_sql_query.replace(word, column_mapping[word])
    
    formatted_dates_1 = extract_and_format_dates(query)
    
    # Check if the query is a count query
    if "how many" in query.lower() and any(keyword in query.lower() for keyword in ["rain", "sun"]):
        count_column = "weather"  # Use the appropriate column name for weather condition
        count_query = f"SELECT COUNT(*) FROM weather_data WHERE {count_column} LIKE '%%{formatted_dates_1[0]}%%';"
        return count_query
    elif "average" in query.lower():
        # Check if the query is related to temperature
        if "temperature" in query.lower():
            avg_column = "temp_max"  # Use the appropriate column name for temperature
            avg_column = "temp_min"
            avg_query = f"SELECT AVG(CAST({avg_column} AS Float)) FROM weather_data;"
            return avg_query
        else:
            raise ValueError("Unsupported average query")
    else:
        return generated_sql_query  # Your existing query
    
    outputs = model.generate(inputs)
    generated_sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print('\n\nmainmian',generated_sql_query)
    generated_sql_query = generated_sql_query.replace("table", "weather_data")
    
    for word in column_mapping.keys():
        generated_sql_query = generated_sql_query.replace(word, column_mapping[word])
    
    formatted_dates_1 = extract_and_format_dates(query)
    print('\n om',formatted_dates_1)
    doc = nlp(query)
    for ent, formatted_date in zip(doc.ents, formatted_dates_1):
        if ent.label_ == "DATE":
            if formatted_dates_1:
                formatted_date_with_year = convert_date_format(formatted_date)  # Format date in SQL query
                print('\n dai',formatted_date_with_year)
                # Add the year to the formatted date
                # formatted_date_with_year += formatted_date.split('-')[-1]
                print('\n formatted_dates_1',formatted_dates_1[0])
                print('\n formatted_date_with_year',formatted_date)
                generated_sql_query = generated_sql_query.replace(f"'{formatted_dates_1}'", f"'{formatted_date_with_year}'")
                print('\n\n out query',generated_sql_query)
            else:
                raise ValueError("Invalid date format in the input")
    generated_sql_query += ";"

    if "average" in query.lower():
        # Check if the query is related to temperature
        if "temperature" in query.lower():
            avg_column = "temp_max"  # Use the appropriate column name for temperature
            avg_column = "temp_min"
            avg_query = f"SELECT AVG(CAST({avg_column} AS Float)) FROM weather_data;"
            return avg_query
        else:
            raise ValueError("Unsupported average query")
    else:
        return generated_sql_query  # Your existing query

    return generated_sql_query

# -----------------------------------------------------

# Function to execute SQL queries against PostgreSQL
def execute_query(sql_query):
    connection = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    cursor = connection.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    connection.close()
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sentence = request.form['sentence']
        print('this is sebtabce',sentence)
        # Use your T5 model to convert the sentence into an SQL query
        sql_query = get_sql(sentence)

        # Execute the SQL query
        results = execute_query(sql_query)

        return render_template('result1.html', sentence=sentence, sql_query=sql_query, results=results)

    return render_template('index1.html')

if __name__ == '__main__':
    app.run(debug=True)
