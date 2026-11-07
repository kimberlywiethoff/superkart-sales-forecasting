import os

import pandas as pd
import requests
import streamlit as st

# Backend address: the Flask container name on the shared Docker network
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860").rstrip("/")

st.set_page_config(page_title="SuperKart Sales Forecaster", page_icon="🛒", layout="centered")
st.title("🛒 SuperKart Sales Forecaster")
st.write(
    "Forecast the total sales revenue of a product in a SuperKart store, "
    "for a single product or a whole batch."
)

online_tab, batch_tab = st.tabs(["Online prediction", "Batch prediction"])

# ------------------------------------------------------------------ Online
with online_tab:
    st.subheader("Product details")
    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
        product_sugar = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
        product_area = st.number_input("Allocated display area (ratio)", min_value=0.0, max_value=1.0,
                                       value=0.068, step=0.001, format="%.3f")
        product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=147.0, step=0.01)
        product_id_char = st.selectbox(
            "Product category code", ["FD", "DR", "NC"],
            help="FD = food, DR = drinks, NC = non-consumables",
        )
    with col2:
        product_type_category = st.selectbox("Product type category", ["Perishables", "Non Perishables"])
        store_size = st.selectbox("Store size", ["Small", "Medium", "High"], index=1)
        store_city = st.selectbox("Store city type", ["Tier 1", "Tier 2", "Tier 3"], index=1)
        store_type = st.selectbox(
            "Store type",
            ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"],
            index=1,
        )
        store_age = st.number_input("Store age (years)", min_value=0, max_value=100, value=16, step=1)

    payload = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": product_sugar,
        "Product_Allocated_Area": product_area,
        "Product_MRP": product_mrp,
        "Store_Size": store_size,
        "Store_Location_City_Type": store_city,
        "Store_Type": store_type,
        "Product_Id_char": product_id_char,
        "Store_Age_Years": int(store_age),
        "Product_Type_Category": product_type_category,
    }

    if st.button("Predict sales", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                prediction = response.json()["Predicted Sales (in dollars)"]
                st.success(f"Forecast sales revenue: ${prediction:,.2f}")
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not reach the backend at {BACKEND_URL}: {exc}")

# ------------------------------------------------------------------ Batch
with batch_tab:
    st.write(
        "Upload a CSV with the columns: Product_Weight, Product_Sugar_Content, Product_Allocated_Area, "
        "Product_MRP, Store_Size, Store_Location_City_Type, Store_Type, Product_Id_char, "
        "Store_Age_Years, Product_Type_Category."
    )
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.dataframe(batch_df.head())

        if st.button("Predict batch", type="primary"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={"file": ("batch.csv", uploaded_file.getvalue(), "text/csv")},
                    timeout=120,
                )
                if response.status_code == 200:
                    preds = response.json()
                    batch_df["Predicted_Sales"] = [preds[str(i)] for i in range(len(batch_df))]
                    st.success(
                        f"Forecast {len(batch_df)} rows – total forecast revenue: "
                        f"${batch_df['Predicted_Sales'].sum():,.2f}"
                    )
                    st.dataframe(batch_df)
                    st.download_button(
                        "Download predictions",
                        batch_df.to_csv(index=False).encode("utf-8"),
                        file_name="superkart_predictions.csv",
                        mime="text/csv",
                    )
                else:
                    st.error(f"API error {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as exc:
                st.error(f"Could not reach the backend at {BACKEND_URL}: {exc}")
