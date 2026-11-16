
import streamlit as st
import pandas as pd
from frontend.api.client import request

st.title("Dashboard Admin")
st.caption("Monitoring Sistem Kontrol Akses APD")

token = st.session_state.token

try:
    pekerja = request("GET", "/pekerja/", token=token, params={"limit": 100}) or []
    devices = request("GET", "/devices/", token=token) or []
    logs = request("GET", "/logs/", token=token, params={"limit": 100}) or []

    total_pekerja = len(pekerja)
    total_device = len(devices)
    online = sum(d["status_perangkat"] for d in devices)
    diterima = sum(log["keputusan_akses"] is True for log in logs)
    ditolak = sum(log["keputusan_akses"] is False for log in logs)

    # METRIC BENTO
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.caption("👥 Total Pekerja")
            st.metric("", total_pekerja)

    with col2:
        with st.container(border=True):
            st.caption("📡 Device Online")
            st.metric("", f"{online}/{total_device}")

    with col3:
        with st.container(border=True):
            st.caption("🟢 Akses Diterima")
            st.metric("", diterima)

    with col4:
        with st.container(border=True):
            st.caption("🔴 Akses Ditolak")
            st.metric("", ditolak)

    # CONTENT BENTO
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.container(border=True):
            st.subheader("📱 Status Perangkat")
            if devices:
                st.dataframe(
                    pd.DataFrame(devices),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "id_device": "Device ID",
                        "waktu_request_terakhir": "Last Heartbeat",
                        "kualitas_rssi_perangkat": "RSSI (dBm)",
                        "status_perangkat": st.column_config.CheckboxColumn("Online"),
                    },
                )
            else:
                st.info("Belum ada perangkat.")

    with col2:
        with st.container(border=True):
            st.subheader("📊 Statistik Akses")
            st.bar_chart(pd.DataFrame({
                "Jumlah": [diterima, ditolak]
            }, index=["Diterima", "Ditolak"]))

    # LOG BENTO
    with st.container(border=True):
        st.subheader("📋 Aktivitas Akses Terbaru")
        if logs:
            st.dataframe(
                pd.DataFrame(logs).head(10),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Belum ada aktivitas akses.")

    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

except Exception as e:
    st.error(f"Gagal mengambil data dashboard: {e}")
