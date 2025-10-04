import streamlit as st
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
import pandas as pd
import pickle

# -----------------------------
# Load Model and Encoders
# -----------------------------
model = tf.keras.models.load_model('my_model.h5')

with open('label_encoder_gender.pkl', 'rb') as file:
    label_encoder_gender = pickle.load(file)

with open('onehot_encoder_geo.pkl', 'rb') as file:
    onehot_encoder_geo = pickle.load(file)

with open('scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

# -----------------------------
# Streamlit App Title
# -----------------------------
st.title("🏦 BANK CUSTOMER CHURN PREDICTION (ANN Classification)")
st.markdown("Predict whether a customer is likely to leave the bank using a trained Artificial Neural Network model.")

# -----------------------------
# User Input Section
# -----------------------------
with st.form("customer_input_form"):
    st.subheader("📋 Enter Customer Details")

    col1, col2 = st.columns(2)
    with col1:
        geography = st.selectbox('🌍 Geography', onehot_encoder_geo.categories_[0])
        gender = st.selectbox('🧍 Gender', label_encoder_gender.classes_)
        age = st.slider('🎂 Age', 18, 92, 30)
        tenure = st.slider('📆 Tenure (Years with Bank)', 0, 10, 5)
        num_of_products = st.slider('🛍️ Number of Products', 1, 4, 1)
    with col2:
        credit_score = st.number_input('💳 Credit Score', min_value=300, max_value=900, value=600)
        balance = st.number_input('💰 Account Balance', value=50000.0)
        estimated_salary = st.number_input('💼 Estimated Salary', value=70000.0)
        has_cr_card = st.selectbox('💳 Has Credit Card?', [0, 1])
        is_active_member = st.selectbox('✅ Is Active Member?', [0, 1])

    # Submit button inside form
    submit_button = st.form_submit_button(label="📨 Submit Details")

# -----------------------------
# Process input when submitted
# -----------------------------
if submit_button:
    st.success("✅ Details submitted successfully! You can now click **Predict** below to get the churn probability.")

    # Prepare input data
    input_data = pd.DataFrame({
        'CreditScore': [credit_score],
        'Gender': [label_encoder_gender.transform([gender])[0]],
        'Age': [age],
        'Tenure': [tenure],
        'Balance': [balance],
        'NumOfProducts': [num_of_products],
        'HasCrCard': [has_cr_card],
        'IsActiveMember': [is_active_member],
        'EstimatedSalary': [estimated_salary]
    })

    # One-hot encode 'Geography'
    geo_encoded = onehot_encoder_geo.transform([[geography]]).toarray()
    geo_encoded_df = pd.DataFrame(
        geo_encoded, 
        columns=onehot_encoder_geo.get_feature_names_out(['Geography'])
    )

    # Combine and scale input
    input_data = pd.concat([input_data.reset_index(drop=True), geo_encoded_df], axis=1)
    input_data_scaled = scaler.transform(input_data)

    # Store for prediction
    st.session_state['input_data_scaled'] = input_data_scaled

# -----------------------------
# Prediction Section
# -----------------------------
if st.button("🔮 Predict"):
    if 'input_data_scaled' in st.session_state:
        input_data_scaled = st.session_state['input_data_scaled']

        # Make prediction
        prediction = model.predict(input_data_scaled)
        prediction_proba = prediction[0][0]

        # Display results beautifully
        st.markdown("---")
        st.subheader("📊 Prediction Results")
        st.metric(label="Churn Probability", value=f"{prediction_proba:.2%}")

        if prediction_proba > 0.5:
            st.error("⚠️ The customer is **likely to churn**.")
        else:
            st.success("✅ The customer is **not likely to churn**.")
    else:
        st.warning("⚠️ Please submit the customer details first.")
