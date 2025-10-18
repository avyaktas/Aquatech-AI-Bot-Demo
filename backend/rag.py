# Load folder and covert into langchain friendly documents
# DirectoryLoader: finds matching files
# PyPDFLoader: extracts text from PDF
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
# long texts -> chunks 
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Next two lines should be for embeddings/storage
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

# Load enviroment
load_dotenv()

#Steps and walkthrough

# Step 1
# Load pdfs from "docs" folder
pdf_loader = DirectoryLoader(
    path="docs", glob="*.pdf", 
    loader_cls=PyPDFLoader)

documents = pdf_loader.load()

#print(f"✅ Loaded {len(documents)} PDF documents.")

# debugging
#if len(documents) == 0:
    #print("No PDF documents found or failed to load.")
#else:
    #print(f"Loaded {len(documents)} PDF documents.")

# Step 2 
# Splits up documents into easier-to-read chunks (startign with 1000 words per chunk)
splitting = RecursiveCharacterTextSplitter(
    chunk_size = 750,  # splits chunks into 1000 words each
    chunk_overlap = 100, #overlap for leniency
    separators = ["\n\n", "\n"]  # Tries to split by paragraph, line (had sentence and words but it didnt make sense so took out)
)

chunks = splitting.split_documents(documents)

#print(f"Split {len(documents)} doc(s) into {len(chunks)} chunks.")
#print("Example chunk:")
#print(chunks[0].page_content[:500])  #sample

# Step 3
# Converting the ext to embeddings
# Takes chunks from step 2 and turns them into vectors (list of numbers representing each chunk)
# This list is an embedding
embeddings = OpenAIEmbeddings() # Uses OpenAIs embedding model

# Step 4
# Store in FAISS index (Facebook Ai similarity Search)
# Fastest way to store and search through chunk vectors

db = FAISS.from_documents(chunks, embeddings) # database

# Step 5
# Save to disk
# Saves so you don thave to reupload every file always, remembers the docs
# Saved in the "faiss_index" folder
db.save_local("faiss_index") 



