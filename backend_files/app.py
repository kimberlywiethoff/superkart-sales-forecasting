import os

import joblib
import pandas as pd
from flask import Flask, jsonify, request

# Initialise the Flask application
superkart_api = Flask("SuperKart Sales Forecaster")

# Load the serialized model pipeline (preprocessing + XGBoost) once at start-up
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "superkart_model.joblib")
model = joblib.load(MODEL_PATH)

# Features the model expects, in training order
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]
NUMERIC_FEATURES = ["Product_Weight", "Product_Allocated_Area", "Product_MRP", "Store_Age_Years"]


def prepare_input(df):
    """Keep the model features in order and coerce numeric columns."""
    df = df[FEATURES].copy()
    for col in NUMERIC_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="raise")
    return df


@superkart_api.get("/")
def home():
    """Health check / landing route."""
    return "Welcome to the SuperKart Sales Forecasting API!"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Online inference: forecast sales for a single product-store record sent as JSON."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be a JSON object."}), 400

    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    try:
        sample = prepare_input(pd.DataFrame([data]))
    except (ValueError, TypeError) as exc:
        return jsonify({"error": f"Invalid input: {exc}"}), 400

    prediction = float(model.predict(sample)[0])
    return jsonify({"Predicted Sales (in dollars)": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Batch inference: forecast sales for every row of an uploaded CSV file."""
    file = request.files.get("file")
    if file is None:
        return jsonify({"error": "Upload a CSV file in the 'file' form field."}), 400

    try:
        batch = pd.read_csv(file)
    except Exception as exc:  # malformed / empty file
        return jsonify({"error": f"Could not read CSV: {exc}"}), 400

    missing = [f for f in FEATURES if f not in batch.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    try:
        predictions = model.predict(prepare_input(batch))
    except (ValueError, TypeError) as exc:
        return jsonify({"error": f"Invalid input: {exc}"}), 400

    # Key = row index of the uploaded file, value = forecast sales
    result = {str(idx): round(float(pred), 2) for idx, pred in zip(batch.index, predictions)}
    return jsonify(result)


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
