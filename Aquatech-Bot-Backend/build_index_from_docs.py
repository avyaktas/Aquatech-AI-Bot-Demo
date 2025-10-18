# This file will load everythign in the docs folder, chink it, embed it, and overwrite FAISS folder
import os 
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredHTMLLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings   # <-- same as ask.py
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
load_dotenv()
ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"

ACTIVE_INDEX_DIR = ROOT / "faiss_index" # Which index to rewrite

def loadFile(path: Path):
    ext = path.suffix.lower()
    if ext == ".pdf":
        return PyPDFLoader(str(path)).load()
    if ext == ".docx":
        return Docx2txtLoader(str(path)).load()
    if ext in (".txt", ".md"):
        return TextLoader(str(path), encoding = "utf-8").load()
    if ext in (".html", ".htm"):
        return UnstructuredHTMLLoader(str(path)).load()
    print(f"File Unsupported: {path.name}")
    return {}

def loadAllDocs(doc_dir: Path): 
    docs = []
    for p in sorted(doc_dir.rglob("*")):
        if p.is_file():
            try:
                docs.extend(loadFile(p))
            except Exception as e:
                print(f"Could not load file {p.name}: {e}")
    return docs

def main(): 
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY. NOT SET")
    if not DOCS_DIR.exists():
        print(f"Docs not found at {DOCS_DIR}")

    raw_docs = loadAllDocs(DOCS_DIR)
    print(f"Loaded {len(raw_docs)} documents from {DOCS_DIR}")

    if not raw_docs: 
        print("No documents found. Put files into docs folder and re-run")
        return
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000, 
        chunk_overlap = 150,
        separators = ["\n\n", "\n"]
    )

    chunks = splitter.split_documents(raw_docs)
    print(f"Split into {len(chunks)} chunks")

    embeddings = OpenAIEmbeddings()
    print("Building FAISS index")

    vectordb = FAISS.from_documents(chunks, embeddings)

    ACTIVE_INDEX_DIR.mkdir(parents = True, exist_ok = True)
    vectordb.save_local(str(ACTIVE_INDEX_DIR))
    print(f"Saved index to: {ACTIVE_INDEX_DIR}")

if __name__ == "__main__": 
    main()


               


    