
import streamlit as st
from frontend.api.client import request

st.title("Konfigurasi Deteksi")

token = st.session_state.token

try:
    current = request(
        "GET",
        "/deteksi/",
        token=token
    )

    if isinstance(current, list):
        current = current[0] if current else {}

    if not current:
        st.warning("Konfigurasi tidak ditemukan.")
        st.stop()

    st.subheader("Parameter YOLO")

    with st.form("update_config"):
        model_path = st.text_input(
            "Model Path",
            value=current.get("model_path", "best.pt")
        )

        image_size = st.select_slider(
            "Image Size",
            options=[320, 416, 512, 640, 768, 960, 1280],
            value=current.get("image_size", 640)
        )

        iou = st.slider(
            "IoU Threshold",
            min_value=0.0,
            max_value=1.0,
            value=float(current.get("iou", 0.45)),
            step=0.01
        )

        conf = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=float(current.get("conf", 0.5)),
            step=0.01
        )

        classes = st.text_input(
            "Classes (ID dipisahkan koma)",
            value=",".join(map(str, current.get("classes") or []))
        )

        minimum_vote = st.slider(
            "Minimum Vote Foto",
            min_value=1,
            max_value=10,
            value=int(current.get("minimum_vote_foto", 1))
        )

        st.caption(f"IoU: {iou} | Confidence: {conf}")

        submitted = st.form_submit_button("Simpan Konfigurasi")

        if submitted:
            try:
                class_list = [
                    int(x.strip())
                    for x in classes.split(",")
                    if x.strip()
                ]

                data = {
                    "id": current["id"],
                    "model_path": model_path,
                    "image_size": image_size,
                    "iou": iou,
                    "conf": conf,
                    "classes": class_list,
                    "minimum_vote_foto": minimum_vote
                }

                request(
                    "PATCH",
                    "/deteksi/",
                    token=token,
                    json=data
                )

                st.success("Konfigurasi berhasil diperbarui!")
                st.rerun()

            except Exception as e:
                st.error(f"Gagal update konfigurasi: {e}")

except Exception as e:
    st.error(f"Gagal mengambil konfigurasi: {e}")
