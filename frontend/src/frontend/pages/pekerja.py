import streamlit as st
import websocket
import threading
import queue
import json

from streamlit_autorefresh import st_autorefresh
from frontend.api.client import request

WS_URL = "wss://api.gabrielsaditya-studio.my.id/scan-ws/ws"


def listen_rfid(rfid_queue):
    def on_message(ws, message):
        try:
            data = json.loads(message)
            rfid_queue.put(data)
        finally:
            ws.close()

    ws = websocket.WebSocketApp(
        WS_URL,
        on_message=on_message,
        on_error=lambda ws, error: rfid_queue.put({"error": str(error)})
    )

    ws.run_forever()

st.title("Manajemen Pekerja")
token = st.session_state.token
col1, col2 = st.columns([3, 1])

with col1:
    search = st.text_input("Cari pekerja")

with col2:
    limit = st.selectbox("Data per halaman", [5, 10, 20, 50], index=1)

if "offset" not in st.session_state:
    st.session_state.offset = 0

try:
    workers = request(
        "GET",
        "/pekerja/",
        token=token,
        params={
            "offset": st.session_state.offset,
            "limit": limit,
            "search": search or None
        }
    )

    st.subheader(f"Data Pekerja ({len(workers)})")
    st.dataframe(workers, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Previous", disabled=st.session_state.offset == 0):
            st.session_state.offset = max(0, st.session_state.offset - limit)
            st.rerun()

    with col2:
        if st.button("Next", disabled=len(workers) < limit):
            st.session_state.offset += limit
            st.rerun()

except Exception as e:
    st.error(f"Gagal mengambil data: {e}")

with st.expander("Tambah Pekerja"):

    if "rfid_queue" not in st.session_state:
        st.session_state.rfid_queue = queue.Queue()

    if "rfid_listening" not in st.session_state:
        st.session_state.rfid_listening = False

    if "rfid_uid_input" not in st.session_state:
        st.session_state.rfid_uid_input = ""

    if st.button("Scan RFID"):
        if not st.session_state.rfid_listening:
            st.session_state.rfid_listening = True

            threading.Thread(
                target=listen_rfid,
                args=(st.session_state.rfid_queue,),
                daemon=True
            ).start()

    if st.session_state.rfid_listening:
        st.info("Menunggu kartu RFID...")
        st_autorefresh(interval=500, key="rfid_refresh")

    try:
        data = st.session_state.rfid_queue.get_nowait()

        st.session_state.rfid_listening = False

        if "error" in data:
            st.error(data["error"])
        else:
            st.session_state.rfid_uid_input = data["uid_rfid"]
            st.success("RFID berhasil terbaca!")

    except queue.Empty:
        pass

    with st.form("create_worker"):
        name = st.text_input("Nama")

        rfid_uid = st.text_input(
            "RFID UID",
            key="rfid_uid_input"
        )

        role = st.text_input("Role")
        is_active = st.checkbox("Aktif", value=True)

        if st.form_submit_button("Tambah"):
            try:
                request(
                    "POST",
                    "/pekerja/",
                    token=token,
                    json={
                        "name": name,
                        "rfid_uid": rfid_uid,
                        "role": role,
                        "is_active": is_active
                    }
                )

                st.success("Pekerja berhasil ditambahkan")
                st.rerun()

            except Exception as e:
                st.error(str(e))

with st.expander("Edit Pekerja"):
    try:
        all_workers = request(
            "GET",
            "/pekerja/",
            token=token,
            params={"offset": 0, "limit": 1000}
        )

        if all_workers:
            selected = st.selectbox(
                "Pilih pekerja",
                all_workers,
                format_func=lambda w: f"{w['name']} ({w['rfid_uid']})"
            )

            with st.form("update_worker"):
                new_name = st.text_input("Nama", value=selected["name"])
                new_uid = st.text_input("RFID UID", value=selected["rfid_uid"])
                new_role = st.text_input("Role", value=selected["role"])
                new_active = st.checkbox("Aktif", value=selected["is_active"])

                if st.form_submit_button("Update"):
                    request(
                        "PATCH",
                        f"/pekerja/{selected['id']}",
                        token=token,
                        json={
                            "name": new_name,
                            "rfid_uid": new_uid,
                            "role": new_role,
                            "is_active": new_active
                        }
                    )
                    st.success("Pekerja berhasil diperbarui")
                    st.rerun()

    except Exception as e:
        st.error(str(e))

with st.expander("Hapus Pekerja"):
    try:
        all_workers = request(
            "GET",
            "/pekerja/",
            token=token,
            params={"offset": 0, "limit": 1000}
        )

        if all_workers:
            selected_delete = st.selectbox(
                "Pilih pekerja",
                all_workers,
                format_func=lambda w: f"{w['name']} ({w['rfid_uid']})",
                key="delete_worker"
            )

            confirm = st.checkbox("Saya yakin ingin menghapus pekerja")

            if st.button("Hapus", type="primary"):
                if confirm:
                    request(
                        "DELETE",
                        f"/pekerja/{selected_delete['id']}",
                        token=token
                    )
                    st.success("Pekerja berhasil dihapus")
                    st.rerun()
                else:
                    st.warning("Konfirmasi penghapusan terlebih dahulu")

    except Exception as e:
        st.error(str(e))
