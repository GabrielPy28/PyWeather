# ETL With Python + Airflow and AWS S3
> Mini program designed to execute ETL (Extract, Transform, Load) processes using a combination of technologies. This application takes advantage of the [OpenWeather](https://openweathermap.org/) API to obtain weather data, [Apache Airflow](https://airflow.apache.org/) to organize and schedule workflows, and [AWS S3](https://aws.amazon.com/es/s3/) to store the transformed data.
>
> ![PyWeather](https://www.bing.com/images/create/pyweather-mini-programa-ejecutar-procesos-etl-api-/1-659a1411c84a42a19647bb5def6455c4?id=pA9FQMZyeicybD6CqRoSog%3d%3d&view=detailv2&idpp=genimg&idpclose=1&FORM=SYDBIC)

## First Steps:
> [!IMPORTANT]
> Some modules, such as the Apache Airflow pwd, may not work very well on Windows; Windows users can try using [WSL](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-10#1-overview) or running it in a Docker container.

1. Install and Create a virtualenv
```
 sudo apt-get install python-pip
 pip install virtualenv
 virtualenv virtualenv_name
 source  virtualenv_name/bin/activate 
```

2. Install dependencies
```
pip install pandas
pip install s3fs
pip install apache-airflow
pip install apache-airflow[cncf.kubernetes] # to resolve any dependencies on kubernetes modules
pip install virtualenv # to resolved ani dependencies on virtualenv modules
```

3. Run Apache Airflow service
```
airflow db migrate

airflow users create \
    --username admin \
    --firstname 'firstname' \
    --lastname 'lastname' \
    --role Admin \
    --email youremail@example.org

airflow webserver --port 8080
```

4. Open another terminal and run the following command: 
```
airflow scheduler
```
> [!NOTE]
> If everything is working correctly, open your browser with http://localhost:8080

5. Creat a New Connection in Airflow:
- Navigation bar  
    - Admin -> Connections 
        - Add new connection
            - Conn Id : weathermap_api         
            - Conn Type : HTTP       
            - Host: https://api.openweathermap.org

6. Copy the dags folder and pasted into the airflow folder:
```
- airflow
    - dags (this will replace old dags)
        - weather_dag.py
```

7. Complete the code in the weather_dag.py file with your own Access Keys, Secrets Keys and Personal Data

8. In the same directory as weather_dag.py, execute the following commands: `python3 weather_dag.py`

> [!NOTE]
> If everything is working correctly, The DAG should now appear on the Airflow Web Server