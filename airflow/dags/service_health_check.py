from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging
import requests

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'ml-ops',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'diabetes_service_health_check',
    default_args=default_args,
    schedule_interval='*/15 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['monitoring'],
)

def check_service_health():
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code != 200:
            raise Exception(f"Status: {response.status_code}")
        logger.info("Service healthy")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise

def check_mlflow_connection():
    try:
        response = requests.get('http://mlflow:5000/api/2.0/mlflow/experiments/list', timeout=5)
        if response.status_code != 200:
            raise Exception(f"Status: {response.status_code}")
        logger.info("MLflow accessible")
        return {"mlflow": "ok"}
    except Exception as e:
        logger.error(f"MLflow failed: {str(e)}")
        raise

def test_prediction():
    try:
        data = {
            "age": 45.0, "sex": 1, "bmi": 25.5, "bp": 120.0,
            "s1": 200.0, "s2": 130.0, "s3": 50.0, "s4": 4.0,
            "s5": 2.5, "s6": 100.0
        }
        response = requests.post('http://localhost:8000/api/v1/predict', json=data, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Status: {response.status_code}")
        logger.info(f"Prediction ok: {response.json()}")
        return response.json()
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise

t1 = PythonOperator(task_id='health', python_callable=check_service_health, dag=dag)
t2 = PythonOperator(task_id='mlflow', python_callable=check_mlflow_connection, dag=dag)
t3 = PythonOperator(task_id='predict', python_callable=test_prediction, dag=dag)

[t1, t2] >> t3
