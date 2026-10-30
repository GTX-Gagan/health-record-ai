import streamlit as st

from exceptions import ApplicationError
from ui.components import patient_form


def render_records(service, repository) -> None:
    st.header("Patient records")
    patients = repository.list(st.text_input("Search by name or email"))
    if not patients:
        st.info("No patient records found.")
        return
    for patient in patients:
        with st.expander(f"{patient.full_name} · {patient.email}"):
            st.write(f"DOB: {patient.date_of_birth:%d/%m/%Y}")
            st.write(f"Glucose: {patient.glucose} | Haemoglobin: {patient.haemoglobin} | Cholesterol: {patient.cholesterol}")
            st.caption(f"AI status: {patient.ai_status}")
            if patient.remarks:
                st.code(patient.remarks, language="json")
                st.caption("AI-generated health-risk indication only; not a medical diagnosis.")
            if patient.ai_status == "failed":
                st.error(patient.ai_error or "AI analysis failed.")
                if st.button("Retry AI analysis", key=f"retry_{patient.id}"):
                    try:
                        service.retry_ai(patient.id)
                        st.success("AI analysis retry completed.")
                        st.rerun()
                    except ApplicationError as exc:
                        st.error(str(exc))
            with st.form(f"delete_{patient.id}"):
                confirm = st.checkbox("Confirm deletion", key=f"confirm_{patient.id}")
                if st.form_submit_button("Delete") and confirm:
                    service.delete(patient.id)
                    st.rerun()
            data = patient_form(patient, key=f"edit_{patient.id}")
            if data:
                try:
                    service.update(patient.id, data)
                    st.success("Patient updated.")
                    st.rerun()
                except ApplicationError as exc:
                    st.error(str(exc))
