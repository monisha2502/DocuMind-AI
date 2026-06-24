from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai
app = FastAPI()
genai.configure(api_key="")
model = genai.GenerativeModel("gemini-2.5-flash")
UPLOAD_FOLDER = "uploads"
pdf_text = ""
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@app.get("/")
async def home():
    return {"message": "home works"}
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename
    }
@app.get("/read-pdf")
def read_pdf():
    global pdf_text
    pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
    if not pdf_files:
        raise HTTPException(
            status_code=404,
            detail="No PDF found"
        )
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_files[0])
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    pdf_text = text
    doc.close()
    return {
        "filename": pdf_files[0],
        "text": text[:3000]
    }
@app.get("/summarize")
def summarize_pdf():
    pdf_files = [
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.endswith(".pdf")
    ]
    if not pdf_files:
        raise HTTPException(
            status_code=404,
            detail="No PDF found"
        )
    pdf_path = os.path.join(
        UPLOAD_FOLDER,
        pdf_files[0]
    )
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    response = model.generate_content(
        f"""
        summarize the following PDF in bullet points.
        Mention:
        - Title
        - Objective
        - Methodology
        - Results
        - Conclusion
        Text:
        {text[:3000]}
        """

    )
    summary = response.text
    return {
        "filename": pdf_files[0],
        "summary": summary
    }

@app.get("/chunk-pdf")
def chunk_pdf():
    pdf_files = [
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.endswith(".pdf")
    ]
    if not pdf_files:
        raise HTTPException(
            status_code=404,
            detail="No PDF found"
        )
    pdf_path = os.path.join(
        UPLOAD_FOLDER,
        pdf_files[0]
    )
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_text(text)
    return {
        "total_chunks": len(chunks),
        "first_chunk": chunks[0]
    }
@app.get("/ask")
def ask_question(question: str):
    if not pdf_text:
        raise HTTPException(
            status_code=400,
            detail="No PDF loaded"
        )
    response = model.generate_content(
        f"""
        Answer the question based only on the PDF content.
        PDF:
        {pdf_text[:5000]}
        Question:
        {question}
        """
    )
    return {
        "question": question,
        "answer": response.text
    }