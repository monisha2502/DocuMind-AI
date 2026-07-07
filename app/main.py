from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import fitz
import yake
import math
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from collections import Counter
from fastapi.responses import FileResponse


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

@app.get("/keywords")
def extract_keywords():
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
    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=2,
        top=10
    )
    keywords = kw_extractor.extract_keywords(text)
    return {
        "filename": pdf_files[0],
        "keywords": [k[0] for k in keywords]
    }

@app.get("/reading-time")
def reading_time():
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
    words = len(text.split())
    minutes = max(1, math.ceil(words / 200))
    return {
        "filename": pdf_files[0],
        "total_words": words,
        "estimated_reading_time": f"{minutes} minute(s)"
    }

@app.get("/word-frequency")
def word_frequency():
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
    words = [
        word.lower()
        for word in text.split()
        if len(word) > 3 and word.isalpha()
    ]
    frequency = Counter(words)
    return {
        "filename": pdf_files[0],
        "top_words": dict(frequency.most_common(15))
    }

@app.get("/metadata")
def pdf_metadata():
    pdf_files = [ f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
    if not pdf_files:
        raise HTTPException(
            status_code=404,
            detail="No PDF found"
        )
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_files[0])
    file_size = round(os.path.getsize(pdf_path) / 1024, 2)
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    result = {
        "filename": pdf_files[0],
        "file_size_kb": file_size,
        "pages": len(doc),
        "title": metadata.get("title"),
        "author": metadata.get("author"),
        "subject": metadata.get("subject"),
        "creator": metadata.get("creator"),
        "producer": metadata.get("producer"),
        "creation_date": metadata.get("creationDate"),
        "modification_date": metadata.get("modDate")
    }
    doc.close()
    return result

@app.get("/search")
def search_pdf(keyword: str):
    pdf_files = [ f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
    if not pdf_files:
        raise HTTPException(
            status_code=404,
            detail="No PDF found"
        )
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_files[0])
    doc = fitz.open(pdf_path)
    results = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if keyword.lower() in text.lower():
            results.append(page_num)
    doc.close()
    return {
        "filename": pdf_files[0],
        "keyword": keyword,
        "found_on_pages": results,
        "total_matches": len(results)
    }

@app.get("/search-context")
def search_context(keyword: str):
    pdf_files = [ f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
    if not pdf_files:
        raise HTTPException(
            status_code=404,
            detail="No PDF found"
        )
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_files[0])
    doc = fitz.open(pdf_path)
    results = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        lines = text.split("\n")
        for line in lines:
            if keyword.lower() in line.lower():
                results.append({
                    "page": page_num,
                    "text": line.strip()
                })
    doc.close()
    return {
        "filename": pdf_files[0],
        "keyword": keyword,
        "results": results,
    }

@app.get("/dashboard")
def dashboard():
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
    words = len(text.split())
    reading_time = f"{max(1, words // 200)} minute(s)"
    file_size = round(os.path.getsize(pdf_path) / 1024, 2)
    metadata = doc.metadata
    doc.close()
    return {
        "filename": pdf_files[0],
        "pages": pages,
        "file_size_kb": file_size,
        "total_words": words,
        "estimated_reading_time": reading_time,
        "author": metadata.get("author"),
        "creator": metadata.get("creator"),
        "producer": metadata.get("producer")
    }

@app.get("/export-summary")
def export_summary():
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
    doc.close()
    parser = PlaintextParser.from_string(
        text,
        Tokenizer("english")
    )
    summarizer = LsaSummarizer()
    summary = ""
    for sentence in summarizer(parser.document, 5):
        summary += str(sentence) + "\n"
    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    return FileResponse(
        "summary.txt",
        media_type="text/plain",
        filename="summary.txt"
    )


               

