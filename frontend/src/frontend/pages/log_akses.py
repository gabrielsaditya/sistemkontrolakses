
import streamlit as st
import pandas as pd
from frontend.api.client import request

st.title("Log Akses")
token = st.session_state.token

col1, col2 = st.columns([3, 1])

with col1:
    search = st.text_input("Cari nama pekerja / RFID")

with col2:
    limit = st.selectbox("Data per halaman", [5, 10, 20, 50], index=1)

if "log_offset" not in st.session_state:
    st.session_state.log_offset = 0

try:
    logs = request(
        "GET",
        "/logs/",
        token=token,
        params={
            "offset": st.session_state.log_offset,
            "limit": limit,
            "search": search or None
        }
    )

    st.subheader(f"Data Log ({len(logs)})")

    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Previous",
                disabled=st.session_state.log_offset == 0
            ):
                st.session_state.log_offset = max(
                    0, st.session_state.log_offset - limit
                )
                st.rerun()

        with col2:
            if st.button("Next", disabled=len(logs) < limit):
                st.session_state.log_offset += limit
                st.rerun()

    else:
        st.info("Tidak ada log akses.")

except Exception as e:
    st.error(f"Gagal mengambil log: {e}")

# DETAIL LOG
with st.expander("Detail Log"):
    try:
        all_logs = request(
            "GET",
            "/logs/",
            token=token,
            params={"offset": 0, "limit": 1000}
        )

        if all_logs:
            selected = st.selectbox(
                "Pilih log",
                all_logs,
                format_func=lambda log: (
                    f"{log['nama_pekerja']} - {log['tanggal_akses']}"
                )
            )

            st.json(selected)

    except Exception as e:
        st.error(str(e))

# EDIT LOG
with st.expander("Edit Log"):
    try:
        all_logs = request(
            "GET",
            "/logs/",
            token=token,
            params={"offset": 0, "limit": 1000}
        )

        if all_logs:
            selected_edit = st.selectbox(
                "Pilih log untuk diedit",
                all_logs,
                format_func=lambda log: (
                    f"{log['nama_pekerja']} - {log['tanggal_akses']}"
                ),
                key="edit_log"
            )

            with st.form("update_log"):
                uid = st.text_input(
                    "RFID UID", value=selected_edit["uid_rfid"]
                )
                nama = st.text_input(
                    "Nama Pekerja", value=selected_edit["nama_pekerja"]
                )
                keputusan = st.checkbox(
                    "Akses diterima",
                    value=selected_edit["keputusan_akses"]
                )

                if st.form_submit_button("Update"):
                    request(
                        "PATCH",
                        f"/logs/{selected_edit['id']}",
                        token=token,
                        json={
                            "uid_rfid": uid,
                            "nama_pekerja": nama,
                            "keputusan_akses": keputusan
                        }
                    )
                    st.success("Log berhasil diperbarui")
                    st.rerun()

    except Exception as e:
        st.error(f"Gagal edit log: {e}")

# DELETE LOG
with st.expander("Hapus Log"):
    try:
        all_logs = request(
            "GET",
            "/logs/",
            token=token,
            params={"offset": 0, "limit": 1000}
        )

        if all_logs:
            selected_delete = st.selectbox(
                "Pilih log untuk dihapus",
                all_logs,
                format_func=lambda log: (
                    f"{log['nama_pekerja']} - {log['tanggal_akses']}"
                ),
                key="delete_log"
            )

            confirm = st.checkbox("Saya yakin ingin menghapus log")

            if st.button("Hapus Log", type="primary"):
                if confirm:
                    request(
                        "DELETE",
                        f"/logs/{selected_delete['id']}",
                        token=token
                    )
                    st.success("Log berhasil dihapus")
                    st.rerun()
                else:
                    st.warning("Konfirmasi penghapusan terlebih dahulu")

    except Exception as e:
        st.error(f"Gagal hapus log: {e}")
