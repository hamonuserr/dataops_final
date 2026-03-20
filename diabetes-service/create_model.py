#!/usr/bin/env python
"""
Generate a dummy diabetes prediction model
Used when no pre-trained model is available
"""

import joblib
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import load_diabetes

def create_dummy_model():
    """Create and save a simple diabetes model"""
    output_path = Path("/app/models/diabetes_model.joblib")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load the diabetes dataset
    diabetes = load_diabetes()
    X = diabetes.data
    y = diabetes.target
    
    # Train a simple RandomForestRegressor
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X, y)
    
    # Save the model
    joblib.dump(model, output_path)
    print(f"✅ Model saved to {output_path}")
    
    return model

if __name__ == "__main__":
    model = create_dummy_model()
    print(f"Model score on training data: {model.score(load_diabetes().data, load_diabetes().target):.4f}")
