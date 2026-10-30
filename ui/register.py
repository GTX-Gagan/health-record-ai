import streamlit as st

from exceptions import ApplicationError
from ui.components import patient_form


def render_register(service) -> None:
    st.header("Register patient")
    data = patient_form(key="register")
    if data:
        try:
            service.create(data)
            st.success("Patient saved.")
        except ApplicationError as exc:
            st.error(str(exc))
