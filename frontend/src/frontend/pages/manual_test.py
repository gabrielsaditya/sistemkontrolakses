
import streamlit as st
import random
import string
from frontend.api.client import request

st.title("Manual Detection")
st.caption("Upload gambar untuk melakukan deteksi APD secara manual.")

def random_device_id():
    return "TEST_DEVICE_" + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )

def random_uid():
    return ":".join(
        "".join(random.choices("0123456789ABCDEF", k=2))
        for _ in range(4)
    )

col1, col2 = st.columns(2)

with col1:
    if st.button("🧪 TEST: Random Device ID"):
        st.session_state.device_id = random_device_id()

with col2:
    if st.button("🧪 TEST: Random RFID UID"):
        st.session_state.uid_rfid = random_uid()
with st.form("manual_detection_form"):

    device_id = st.text_input(
        "Device ID",
        key="device_id"
    )

    uid_rfid = st.text_input(
        "UID RFID",
        key="uid_rfid"
    )

    images = st.file_uploader(
        "Upload Gambar",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    submitted = st.form_submit_button("Mulai Deteksi")

if submitted:
    if not device_id or not uid_rfid or not images:
        st.warning("Device ID, UID RFID, dan gambar wajib diisi.")
    else:
        try:
            files = [
                ("images", (image.name, image.getvalue(), image.type))
                for image in images
            ]

            result = request(
                "POST",
                "/deteksi/",
                data={
                    "device_id": device_id,
                    "uid_rfid": uid_rfid
                },
                files=files
            )

            st.success("Deteksi berhasil dilakukan!")

            if result["keputusan_akses"]:
                st.success("AKSES DITERIMA")
            else:
                st.error("AKSES DITOLAK")

            st.write("Nama Pekerja:", result["nama_pekerja"])
            st.write("UID RFID:", result["uid_rfid"])
            st.json(result)

        except Exception as e:
            st.error(f"Gagal melakukan deteksi: {e}")
