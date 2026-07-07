import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📄",
    layout="wide"
)

# Theme Toggle
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

theme = st.sidebar.toggle("🌙 Dark Mode", value=True)

if theme:
    bg = "#0E1117"
    text = "white"
    card = "#161B22"
else:
    bg = "#FFFFFF"
    text = "#000000"
    card = "#F5F5F5"

st.markdown(f"""
<style>

.main {{
    background: {bg};
}}

.stApp {{
    background: {bg};
    color: {text};
}}

.block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
}}

h1, h2, h3, h4, h5, h6, p, label, span, div, .stMarkdown, .stText, .stCaption {{
    color: {text} !important;
}}

div.stButton > button {{
    width: 100%;
    border-radius: 12px;
    height: 45px;
    font-weight: bold;
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    color: white;
    border: none;
}}

div.stButton > button:hover {{
    background: #0059ff;
}}

.stDownloadButton > button {{
    width: 100%;
    border-radius: 10px;
    height: 45px;
    background: #16a34a;
    color: white;
    border: none;
}}

.upload-box {{
    padding: 25px;
    border-radius: 15px;
    background: {card};
    border: 1px solid #30363D;
}}

.result-box {{
    background: {card};
    border-radius: 15px;
    padding: 20px;
    border: 1px solid #30363D;
}}

</style>
""", unsafe_allow_html=True)

with st.sidebar:

    st.title("📄 AI Powered PDF Analysis")

    st.markdown("---")

    st.write("### Features")

    st.success("✔ Upload PDF")
    st.success("✔ Metadata")
    st.success("✔ Analytics")
    st.success("✔ Summary")
    st.success("✔ Keyword Search")
    st.success("✔ Search Context")
    st.success("✔ Word Frequency")
    st.success("✔ Top Keywords")
    st.success("✔ Word Cloud")

    st.markdown("---")

    st.info("DocuMind AI")

st.title("📄 AI Powered PDF Analysis")

st.caption("FastAPI + Streamlit + Python")

st.markdown("---")

st.subheader("📤 Upload PDF")

uploaded_file = st.file_uploader(
    "Choose a PDF",
    type=["pdf"]
)




if uploaded_file is not None:

    st.success(f" ✅ Selected File : {uploaded_file.name}")

    if st.button("📤 Upload PDF", use_container_width=True):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf"
            )
        }

        with st.spinner("Uploading PDF..."):

            response = requests.post(
                API + "/upload",
                files=files
            )

        if response.status_code == 200:

            st.balloons()
            st.success("✅ PDF Uploaded Successfully!")

            st.metric(
                "File Size",
                f"{uploaded_file.size/(1024 *1024):.2f} MB"
            )

            st.json(response.json())

            st.download_button(
                "⬇️ Download Analysis",
                data=str(response.json()),
                file_name="analysis.txt",
                mime="text/plain"
            )

        else:

            st.error(response.text)

st.markdown("---")

st.subheader("📑 PDF Analysis")

left, col1, col2, right = st.columns([1,2,2,1])

with col1:

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📝 Metadata", use_container_width=True):

        response = requests.get(API + "/metadata")

        if response.status_code == 200:

            data = response.json()

            st.success("Metadata Retrieved Successfully")

            with st.expander("📄 View Metadata"):
                st.json(data)

            c1, c2 = st.columns(2)

            with c1:
                st.metric("📄 Pages", data.get("pages","N/A"))
                st.metric("👤 Author", data.get("author","Unknown"))
                st.metric("📄 Title", data.get("title","Unknown"))

            with c2:
                st.metric("💾 Size (KB)", round(data.get("file_size_kb",0),2))
                st.metric("📄 File", data.get("filename","N/A"))
                st.metric("🕒 Creator", data.get("creator","Unknown"))

        else:
            st.error(response.text)


with col2:

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📊 Analytics", use_container_width=True):

        response = requests.get(API + "/dashboard")

        if response.status_code == 200:

            data = response.json()

            st.success("✅ Analytics Generated Successfully")

            c1, c2 = st.columns(2)

            with c1:
                st.metric("📄 Pages", data["pages"])
                st.metric("📝 Total Words", data["total_words"])

            with c2:
                st.metric(
                    "💾 File Size",
                    f"{round(data['file_size_kb'],2)} KB"
                )
                st.metric(
                    "⏱ Reading Time",
                    data["estimated_reading_time"]
                )

            st.write("### 📄 File")
            st.info(data["filename"])

            with st.expander("📊 View Complete Analytics"):
                st.json(data)

            st.markdown("---")

            st.subheader("📋 Document Statistics")

            stats = pd.DataFrame({
                "Metric": [
                    "Pages",
                    "Total Words",
                    "Reading Time (Minutes)"
                ],
                "Value": [
                    data["pages"],
                    data["total_words"],
                    int(data["estimated_reading_time"].split()[0])
                ]
            })

            st.dataframe(
                stats,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")

            st.subheader("🥧 Document Composition")

            labels = ["Pages", "Words"]

            sizes = [
                data["pages"],
                data["total_words"]
            ]

            fig, ax = plt.subplots(figsize=(5,5))

            ax.pie(
                sizes,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90
            )

            ax.axis("equal")

            st.pyplot(fig)

            st.markdown("---")

            st.subheader("📌 Quick Overview")

            st.write("📄 Pages")

            st.progress(
                min(data["pages"] / 100, 1.0)
            )

            st.write("📝 Words")

            st.progress(
                min(data["total_words"] / 10000, 1.0)
            )

            minutes = int(
                data["estimated_reading_time"].split()[0]
            )

            st.write("⏱ Reading Time")

            st.progress(
                min(minutes / 60, 1.0)
            )

        else:

            st.error(response.text)

st.markdown("---")

st.subheader("📄 Summary")

if st.button("Generate Summary", use_container_width=True):

    with st.spinner("Generating summary..."):

        response = requests.get(API + "/export-summary")

    if response.status_code == 200:

        summary = response.text

        st.success("✅ Summary Generated Successfully!")

        with st.expander("📄 Preview Summary", expanded=True):

            st.text_area(
                "Generated Summary",
                summary,
                height=250,
                disabled=True
            )

        st.download_button(
            label="⬇️ Download Summary",
            data=summary,
            file_name="summary.txt",
            mime="text/plain",
            use_container_width=True
        )

    else:

        st.error(response.text)

st.markdown("---")

st.subheader("🔍 Keyword Search")

keyword = st.text_input(
    "Enter a keyword",
    placeholder="Example: AI, Python, Machine Learning..."
)

search_col1, search_col2 = st.columns(2)


with search_col1:

    if st.button("🔎 Search Keyword", use_container_width=True):

        if keyword.strip() == "":

            st.warning("Please enter a keyword.")

        else:

            with st.spinner("Searching keyword..."):

                response = requests.get(
                    API + "/search",
                    params={"keyword": keyword}
                )

            if response.status_code == 200:

                data = response.json()

                st.success("✅ Keyword Found")

                st.metric("Keyword", keyword)

                with st.expander("View Result", expanded=True):

                    st.json(data)

            else:

                st.error(response.text)

with search_col2:

    if st.button("📖 Search Context", use_container_width=True):

        if keyword.strip() == "":

            st.warning("Please enter a keyword.")

        else:

            with st.spinner("Searching context..."):

                response = requests.get(
                    API + "/search-context",
                    params={"keyword": keyword}
                )

            if response.status_code == 200:

                data = response.json()

                st.success("✅ Context Retrieved Successfully")

                st.metric("Keyword", keyword)

                with st.expander("View Context", expanded=True):

                    st.json(data)

            else:

                st.error(response.text)

st.markdown("---")

st.subheader("📊 Word Frequency")

if st.button("Show Word Frequency", use_container_width=True):

    with st.spinner("Loading word frequencies..."):

        response = requests.get(API + "/word-frequency")

    if response.status_code == 200:

        data = response.json()

        st.success("✅ Word Frequency Loaded Successfully!")

        words = data["top_words"]

        df = pd.DataFrame(
            list(words.items()),
            columns=["Word", "Frequency"]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            df.set_index("Word")
        )

    else:

        st.error(response.text)

st.markdown("---")

st.subheader("🏷️ Top Keywords")

if st.button("Show Top Keywords", use_container_width=True):

    with st.spinner("Loading keywords..."):

        response = requests.get(API + "/keywords")

    if response.status_code == 200:

        data = response.json()

        st.success("✅ Top Keywords Loaded Successfully!")

        keywords = data["keywords"]

        st.write("### 🏷️ Extracted Keywords")

        for i, word in enumerate(keywords, start=1):
            st.write(f"**{i}.** {word}")

    else:

        st.error(response.text)

st.markdown("---")

st.subheader("☁️ Word Cloud")

if st.button("Generate Word Cloud", use_container_width=True):

    with st.spinner("Generating Word Cloud..."):

        response = requests.get(API + "/word-frequency")

    if response.status_code == 200:

        data = response.json()

        wc = WordCloud(
            width=1200,
            height=600,
            background_color="black",
            colormap="viridis"
        ).generate_from_frequencies(data["top_words"])

        fig, ax = plt.subplots(figsize=(12,6))

        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")

        st.pyplot(fig)

    else:

        st.error(response.text)

st.markdown("---")

st.markdown(
    """
    <hr>

    <center>

    ## 📄 DocuMind AI

    ### AI Powered PDF Analysis System

    🚀 Built using **FastAPI • Streamlit • Python**

    Developed by **Monisha Vignesh**

    </center>

    """,
    unsafe_allow_html=True
)