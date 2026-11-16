import streamlit as st
from frontend.api.client import get_token, register
from frontend.components.sidebar import render_sidebar

pages = [
    st.Page("pages/dashboard.py", title="Dashboard", icon="🦺"),
    st.Page("pages/pekerja.py", title="Manajemen Pekerja", icon="👥"),
    st.Page("pages/log_akses.py", title="Log Akses", icon="📋"),
    st.Page("pages/konfigurasi.py", title="Konfigurasi Deteksi", icon="⚙️"),
    st.Page("pages/devices.py", title="List Device", icon="📱"),
    st.Page("pages/manual_test.py", title='Manual Test', icon="📸")
]


pg = st.navigation(pages, position="hidden")
st.set_page_config(
    page_title="Dashboard Admin Sistem",
    layout="wide"
)

if "token" not in st.session_state:
    st.session_state.token = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.token:
    render_sidebar()
    pg.run()

else:
    if st.session_state.page == "login":
        st.markdown(
            """
    <style>
    [data-testid='stSidebar']{
        display: none;
    }
    </style>
""", unsafe_allow_html=True
        )
        st.title("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            token = get_token(username, password)

            if token:
                st.session_state.token = token
                st.rerun()
            else:
                st.error("Login failed!")

        if st.button("Register"):
            st.session_state.page = "register"
            st.rerun()

    else:
        st.title("Register")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Register"):
            response = register(username, password)

            if response:
                st.success("Registration successful")

        if st.button("Back to Login"):
            st.session_state.page = "login"
            st.rerun()