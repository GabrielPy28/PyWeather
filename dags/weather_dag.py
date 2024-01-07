from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import pandas as pd
from s3fs import S3FileSystem

now = datetime.now()

def kelvin_to_fahrenheit(temp_in_kelvin):
    temp_in_fahrenheit = (temp_in_kelvin - 273.15) * (9/5) + 32
    return temp_in_fahrenheit

def transform_load_data(task_instance):
    data = task_instance.xcom_pull(task_ids='extract_data')
    city = data['name']
    weather_description = data['weather'][0]['description']
    temp_fahrenheit = kelvin_to_fahrenheit(data['main']['temp'])
    feels_temp = kelvin_to_fahrenheit(data['main']['feels_like'])
    min_temp = kelvin_to_fahrenheit(data['main']['temp_min'])
    max_temp = kelvin_to_fahrenheit(data['main']['temp_max'])
    pressure = data['main']['pressure']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    time_record = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
    sunrise_time = datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone'])
    sunset_time = datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone'])

    formated_data = {
        'City': city,
        'Weather Description': weather_description,
        'Temperature (F)': f"{temp_fahrenheit:.2}",
        'Feels Like (F)': f"{feels_temp:.2}",
        'Min. Temperature (F)': f"{min_temp:.2}",
        'Max. Temperature (F)': f"{max_temp:.2}",
        'Pressure': pressure,
        'Humidity %': humidity,
        'Wind Speed MPH': wind_speed,
        'Time Recorded (UTC)': time_record,
        'Sunrise Time (UTC)': sunrise_time,
        'Sunset Time (UTC)': sunset_time
    }

    transformed_data = [formated_data]
    df = pd.DataFrame(transformed_data)

    aws_access_key_id = 'YOUR_ACCESS_KEY_ID'
    aws_secret_access_key = 'YOUR_SECRET_ACCESS_KEY'
    
    s3 = S3FileSystem(key=aws_access_key_id, secret=aws_secret_access_key)
    filename = f'openweathermap_{city}_{now.strftime("%d-%m-%Y_%H:%M")}'

    with s3.open(f's3://YOUR_BUCKET_NAME/{filename}.csv', 'w') as f:
        df.to_csv(f, index=False)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': now.strftime("%Y-%m-%d"),
    'email': ['youremail@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

#Creating the DAG
with DAG(
    'weather_dag',              
    default_args=default_args, 
    schedule_interval='@daily', 
    catchup=False               
) as dag:
    
    # Task to check if the api is ready
    is_api_ready = HttpSensor(
        task_id = 'is_api_ready',
        http_conn_id='weathermap_api',
        endpoint='/data/2.5/weather?q=Portland&appid=YOUR_API_KEY'
    ),

    # Task to get data from OpenWeatherMap API
    extract_data = SimpleHttpOperator(
        task_id = 'extract_data',
        http_conn_id = 'weathermap_api',
        endpoint = '/data/2.5/weather?q=Portland&appid=YOUR_API_KEY',
        method = 'GET',
        response_filter = lambda r: json.loads(r.text),
        log_response = True
    )

    # Task to transform data and upload it to an S3 bucket
    transform_data = PythonOperator(
        task_id="transform_data",
        python_callable=transform_load_data
    )

    is_api_ready >> extract_data >> transform_data