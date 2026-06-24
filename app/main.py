from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
app = FastAPI()
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
    if len(pdf_files) == 0:
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
    parser = PlaintextParser.from_string(
        text,
        Tokenizer("english")
    )
    summarizer = LsaSummarizer()
    summary = ""
    for sentence in summarizer(parser.document, 5):
        summary += str(sentence) + "\n"
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
@app.get("/analytics")
def pdf_analytics():
    pdf_files = [ f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
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
    pages = len(doc)
    doc.close()
    return {
        "filename": pdf_files[0],
        "pages": pages,
        "words": len(text.split()),
        "characters": len(text),
    }
