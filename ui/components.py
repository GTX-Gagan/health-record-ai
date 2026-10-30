import streamlit as st

from database.models import Patient


def patient_form(patient: Patient | None = None, key: str = "patient_form") -> dict | None:
    with st.form(key):
        name = st.text_input("Full name", value=patient.full_name if patient else "")
        dob = st.text_input(
            "Date of birth (dd/mm/yyyy)",
            value=patient.date_of_birth.strftime("%d/%m/%Y") if patient else "",
        )
        email = st.text_input("Email", value=patient.email if patient else "")
        c1, c2, c3 = st.columns(3)
        glucose = c1.text_input("Glucose (mg/dL)", value=str(patient.glucose) if patient else "")
        haemoglobin = c2.text_input("Haemoglobin (g/dL)", value=str(patient.haemoglobin) if patient else "")
        cholesterol = c3.text_input("Cholesterol (mg/dL)", value=str(patient.cholesterol) if patient else "")
        submitted = st.form_submit_button("Save patient", type="primary")
    return {"full_name": name, "date_of_birth": dob, "email": email, "glucose": glucose,
            "haemoglobin": haemoglobin, "cholesterol": cholesterol} if submitted else None
