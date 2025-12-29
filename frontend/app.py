import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:5000/api"

st.set_page_config(
    page_title="Search Engine Skripsi",
    layout="wide"
)

st.title("Search Engine Skripsi")
st.caption("BM25 • Wildcard • Spelling Correction • Bahasa Indonesia")

st.sidebar.header("⚙️ Pengaturan")

mode = st.sidebar.radio(
    "Mode",
    ["Pencarian Skripsi", "Upload Skripsi"]
)

if mode == "Pencarian Skripsi":
    st.subheader("🔍 Pencarian Dokumen")

    query = st.text_input(
        "Masukkan query pencarian",
        placeholder="contoh: rede* website",
        key="input_query"
    )

    if st.button("Cari", type="primary", key="btn_search"):
        if not query.strip():
            st.warning("Query tidak boleh kosong")
        else:
            with st.spinner("🔎 Mencari dokumen..."):
                response = requests.post(
                    f"{API_BASE_URL}/search",
                    json={"query": query}
                )

            if response.status_code != 200:
                st.error("Gagal melakukan pencarian")
            else:
                data = response.json()

                col_a, col_b = st.columns(2)
                col_a.metric(
                    "⏱ Waktu Eksekusi",
                    f"{data['time_ms']} ms"
                )
                col_b.metric(
                    "Total Dokumen",
                    data["total_results"]
                )

                st.divider()

                st.markdown("## 🔄 Proses Query")

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.caption("Original")
                    st.text_area(
                        label="Original Query",
                        value=data["original_query"],
                        height=90,
                        disabled=True,
                        key="query_original"
                    )

                with c2:
                    st.caption("Wildcard")
                    st.text_area(
                        label="Wildcard Query",
                        value=data["wildcard_query"],
                        height=90,
                        disabled=True,
                        key="query_wildcard"
                    )

                with c3:
                    st.caption("Corrected")
                    st.text_area(
                        label="Corrected Query",
                        value=data["corrected_query"],
                        height=90,
                        disabled=True,
                        key="query_corrected"
                    )

                with c4:
                    st.caption("Final")
                    st.text_area(
                        label="Final Query",
                        value=data["final_query"],
                        height=90,
                        disabled=True,
                        key="query_final"
                    )

                st.divider()

                st.markdown(
                    f"## 📄 Hasil Pencarian ({data['total_results']} dokumen)"
                )

                if data["total_results"] == 0:
                    st.info("Tidak ada dokumen yang ditemukan")
                else:
                    for i, doc in enumerate(data["results"], start=1):
                        with st.expander(f"{i}. {doc['title']}"):
                            st.write(f"**Penulis:** {doc['authors']}")
                            st.write(f"**Institusi:** {doc['publisher']}")
                            st.write(f"**BM25 Score:** `{doc['score']}`")

                            if doc.get("pdf_link"):
                                st.markdown(
                                    f"[📄 Unduh PDF]({doc['pdf_link']})"
                                )

elif mode == "Upload Skripsi":
    st.subheader("📤 Upload Dokumen Skripsi")

    title = st.text_input("Judul Skripsi", key="upload_title")
    authors = st.text_input("Penulis", key="upload_authors")
    publisher = st.text_input("Universitas", key="upload_publisher")

    pdf_file = st.file_uploader(
        "Upload file PDF",
        type=["pdf"],
        key="upload_pdf"
    )

    if st.button("Upload", type="primary", key="btn_upload"):
        if not title or not authors or not pdf_file:
            st.warning("Judul, penulis, dan file PDF wajib diisi")
        else:
            with st.spinner("📤 Mengunggah & membangun index..."):
                files = {
                    "pdf": (
                        pdf_file.name,
                        pdf_file,
                        "application/pdf"
                    )
                }

                data = {
                    "title": title,
                    "authors": authors,
                    "publisher": publisher
                }

                response = requests.post(
                    f"{API_BASE_URL}/upload",
                    files=files,
                    data=data
                )

            if response.status_code == 201:
                st.success(" Upload berhasil & index diperbarui")
            else:
                st.error(" Upload gagal")

st.divider()
st.caption("© Search Engine Skripsi — Information Retrieval BM25")
