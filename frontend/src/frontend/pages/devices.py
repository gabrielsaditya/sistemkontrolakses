
import streamlit as st
import pandas as pd
from frontend.api.client import request

st.title("Device Status")
token = st.session_state.token

try:
    devices = request(
        "GET",
        "/devices/",
        token=token,
    )

    if not devices:
        st.warning("Device Tidak Ditemukan")
        st.stop()

    df = pd.DataFrame(devices)

    # Statistik perangkat
    total = len(df)
    online = int(df["status_perangkat"].sum())
    offline = total - online

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Device", total)
    col2.metric("Online", online)
    col3.metric("Offline", offline)

    st.divider()
    st.subheader("Daftar Perangkat")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id_device": "Device ID",
            "waktu_request_terakhir": "Last Heartbeat",
            "kualitas_rssi_perangkat": "RSSI (dBm)",
            "status_perangkat": st.column_config.CheckboxColumn(
                "Online"
            ),
        }
    )

    if st.button("Refresh"):
        st.rerun()

except Exception as e:
    st.error(f"Gagal mengambil data device: {e}")
