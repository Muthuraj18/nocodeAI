from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from flask import Blueprint, render_template

bp = Blueprint('app2', __name__, template_folder='templates', static_folder='static')

@bp.route('/')
def index():
    return render_template('index2.html')

app = Flask(__name__)

# Load the weather dataset
dataset_path = 'seattle-weather.csv'  # Replace with your dataset file path
df = pd.read_csv('app2\seattle-weather.csv')

# Prepare the dataset
X = df[['precipitation', 'temp_max', 'temp_min', 'wind']]
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df['weather'])

# Train a Random Forest classifier
model = RandomForestClassifier()
model.fit(X, y)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        precipitation = float(request.form['precipitation'])
        temp_max = float(request.form['temp_max'])
        temp_min = float(request.form['temp_min'])
        wind = float(request.form['wind'])

        input_data = [[precipitation, temp_max, temp_min, wind]]
        prediction_class = model.predict(input_data)
        predicted_weather = label_encoder.inverse_transform(prediction_class)

        return render_template('index2.html', predicted_weather=predicted_weather[0])
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
