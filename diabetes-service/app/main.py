import logging, json, os, time
from datetime import datetime
from pathlib import Path
from typing import Optional
import traceback
from fastapi import FastAPI, HTTPException, Request
import numpy as np, joblib
from prometheus_client import Counter, Histogram, Gauge
from starlette_exporter import PrometheusMiddleware, handle_metrics
import mlflow
from mlflow import MlflowClient
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from app.schemas import PatientData, PredictionResponse
    from app.model import model_loader
except ImportError:
    logger.warning("Inline imports")
    from pydantic import BaseModel, Field
    
    class PatientData(BaseModel):
        age: float
        sex: int
        bmi: float
        bp: float
        s1: float
        s2: float
        s3: float
        s4: float
        s5: float
        s6: float
    
    class PredictionResponse(BaseModel):
        predict: float
    
    class DummyModelLoader:
        def load_model(self): pass
        def predict(self, features): return np.mean(features) * 0.5 + 50
    
    model_loader = DummyModelLoader()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/diabetes_model.joblib")
MODEL_VERSION = os.getenv("MODEL_VERSION", "2")
LOG_FILE = "/app/logs/requests.jsonl"

Path("/app/logs").mkdir(parents=True, exist_ok=True)
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

prediction_counter = Counter('diabetes_predictions_total', 'Total predictions', ['status', 'model_version'])
prediction_latency = Histogram('diabetes_prediction_latency_seconds', 'Latency', ['status'], buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0))
active_requests = Gauge('diabetes_active_requests', 'Active requests')
mlflow_status_gauge = Gauge('mlflow_connection_status', 'MLflow status')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting - MLflow: {MLFLOW_TRACKING_URI}, Model: {MODEL_VERSION}")
    try:
        model_loader.load_model()
        logger.info("Model loaded")
    except Exception as e:
        logger.error(f"Model load failed: {str(e)}")
    yield
    logger.info("Shutting down")

app = FastAPI(title="Diabetes Prediction", version="1.0.0", lifespan=lifespan)
app.add_middleware(PrometheusMiddleware, app_name="diabetes_service")
app.add_route("/metrics", handle_metrics)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    active_requests.inc()
    start_time = time.time()
    try:
        response = await call_next(request)
        return response
    finally:
        active_requests.dec()

@app.get("/")
async def root():
    return {
        "name": "Diabetes Prediction Service",
        "version": "1.0.0",
        "endpoints": {"/health", "/api/v1/predict", "/metrics", "/mlflow/status"}
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "model_version": MODEL_VERSION, "model_loaded": True}

@app.get("/ready")
async def ready():
    try:
        model_loader.load_model()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Ready check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Not ready")

@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(data: PatientData):
    request_id = datetime.utcnow().isoformat()
    start_time = time.time()
    
    try:
        features = [data.age, data.sex, data.bmi, data.bp, data.s1, data.s2, data.s3, data.s4, data.s5, data.s6]
        prediction = float(model_loader.predict(features))
        latency = time.time() - start_time
        
        prediction_counter.labels(status="success", model_version=MODEL_VERSION).inc()
        prediction_latency.labels(status="success").observe(latency)
        _log_request(request_id, data.dict(), prediction, "success", latency)
        
        try:
            with mlflow.start_run(run_name=f"pred_{request_id}", nested=True):
                mlflow.log_metric("prediction", prediction)
        except:
            pass
        
        logger.info(f"Prediction: {prediction:.2f} ({latency*1000:.2f}ms)")
        return PredictionResponse(predict=round(prediction, 2))
        
    except Exception as e:
        latency = time.time() - start_time
        logger.error(f"Prediction error: {str(e)}")
        prediction_counter.labels(status="error", model_version=MODEL_VERSION).inc()
        prediction_latency.labels(status="error").observe(latency)
        _log_request(request_id, data.dict(), None, "error", latency, str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/v1/batch-predict")
async def batch_predict(data_list: list[PatientData]):
    results = []
    for data in data_list:
        try:
            result = await predict(data)
            results.append({"status": "success", "prediction": result.predict})
        except Exception as e:
            results.append({"status": "error", "error": str(e)})
    
    return {"predictions": results, "total": len(results), "successful": sum(1 for r in results if r["status"] == "success")}

@app.get("/api/v1/model-info")
async def model_info():
    return {
        "version": MODEL_VERSION,
        "path": MODEL_PATH,
        "features": ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"],
        "feature_count": 10
    }

@app.get("/api/v1/stats")
async def stats():
    try:
        if Path(LOG_FILE).exists():
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
            total = len(lines)
            successful = sum(1 for line in lines if '"success"' in line)
        else:
            total, successful = 0, 0
        return {"total": total, "successful": successful, "failed": total - successful}
    except Exception as e:
        logger.warning(f"Stats error: {str(e)}")
        return {"total": 0, "successful": 0, "failed": 0}

@app.get("/mlflow/status")
async def mlflow_status():
    try:
        client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
        experiments = client.search_experiments()
        mlflow_status_gauge.set(1)
        return {"status": "connected", "uri": MLFLOW_TRACKING_URI, "experiments": len(experiments)}
    except Exception as e:
        mlflow_status_gauge.set(0)
        logger.warning(f"MLflow error: {str(e)}")
        return {"status": "disconnected", "uri": MLFLOW_TRACKING_URI, "error": str(e)}

def _log_request(request_id: str, input_data: dict, prediction: Optional[float], status: str, latency: float, error: Optional[str] = None):
    try:
        log_entry = {"request_id": request_id, "timestamp": datetime.utcnow().isoformat(), "status": status, "input": input_data, "prediction": prediction, "latency": latency, "model_version": MODEL_VERSION, "error": error}
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        logger.error(f"Log error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
