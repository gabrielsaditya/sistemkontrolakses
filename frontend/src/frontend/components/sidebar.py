import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div style="text-align:center; margin-bottom:20px;">
                <h3 style="margin-bottom:0;">Dashboard Admin</h3>
                <small>Sistem Kontrol Akses APD</small>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.page_link("pages/dashboard.py", label="Dashboard", icon="🏠")
        st.page_link("pages/pekerja.py", label="Manajemen Pekerja", icon="👥")
        st.page_link("pages/log_akses.py", label="Log Akses", icon="📋")
        st.page_link("pages/konfigurasi.py", label="Konfigurasi Deteksi", icon="⚙️")
        st.page_link("pages/devices.py", label="Device Status", icon="📱")
        st.page_link("pages/manual_test.py", label="Manual Test", icon="📸")

        st.markdown("""
            <style>
            [data-testid="stSidebar"] div.stButton {
                position: fixed;
                bottom: 20px;
                width: 230px;
            }

            [data-testid="stSidebar"] div.stButton button {
                background-color: #dc2626;
                color: white;
                border: none;
                font-weight: bold;
            }

            [data-testid="stSidebar"] div.stButton button:hover {
                background-color: #b91c1c;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()