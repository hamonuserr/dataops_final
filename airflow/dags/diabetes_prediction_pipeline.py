from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'ml-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'diabetes_prediction_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ml', 'prediction'],
)

def extract_data():
    import pandas as pd
    from sklearn.datasets import load_diabetes
    logger.info("Extracting data...")
    diabetes = load_diabetes()
    df = pd.DataFrame(diabetes.data, columns=diabetes.feature_names)
    df['target'] = diabetes.target
    return df.to_dict()

def preprocess_data(**context):
    logger.info("Preprocessing data...")
    return {"status": "ok"}

def train_model(**context):
    import mlflow
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.datasets import load_diabetes
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    
    logger.info("Training model...")
    diabetes = load_diabetes()
    X_train, X_test, y_train, y_test = train_test_split(
        diabetes.data, diabetes.target, test_size=0.2, random_state=42
    )
    
    mlflow.set_experiment("diabetes_experiments")
    with mlflow.start_run():
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("r2", r2)
        logger.info(f"MSE: {mse:.4f}, R2: {r2:.4f}")

def validate_model(**context):
    logger.info("Validating model...")
    return {"status": "passed"}

def register_model(**context):
    logger.info("Registering model...")

t1 = PythonOperator(task_id='extract', python_callable=extract_data, dag=dag)
t2 = PythonOperator(task_id='preprocess', python_callable=preprocess_data, dag=dag)
t3 = PythonOperator(task_id='train', python_callable=train_model, dag=dag)
t4 = PythonOperator(task_id='validate', python_callable=validate_model, dag=dag)
t5 = PythonOperator(task_id='register', python_callable=register_model, dag=dag)

t1 >> t2 >> t3 >> t4 >> t5
