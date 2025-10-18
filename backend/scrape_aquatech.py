# scrapes content from www.Aquatech.com and saves it to FAISS index 
import requests      # lets you download content of websites
from bs4 import BeautifulSoup     # parses and cleants HTML
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
load_dotenv()


# gets text content from webpage
def scrape_webpage(url): 
    headers = {"Use-Agent": "Mozilla/5.0"} # took a while to figure this out- makes it look like request is coming from browser, not a bot
    response = requests.get(url, headers = headers, timeout = 10) # doanloads page from internet
    soup = BeautifulSoup(response.text, 'html.parser') # HTML -> readable structure
    for tag in soup(["script", "style", "header", "footer", "nav"]):   # cleans up unneeded stuff
        tag.decompose()
    text = soup.get_text(separator = '')
    clean_text = ''.join(text.split()) # cleaning
    return clean_text


# scrape several pages and builed FAISS index
def build_aqua_index(urls, index_path="faiss_index_aquatech"):
    docs = []
    for url in urls: 
        print(f"Scraping: {url}")
        page_text = scrape_webpage(url) # uses function to scrap page
        doc = Document(page_content=page_text, metadata={"source": url}) # looked this up- dont fully understand (needed later for chunking and embedding)
        docs.append(doc) #appends to docs list
    # spilts scraped docs into chunks to turn itno embeddings
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
    
   # explainin rag.py
    chunks = splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings() 
    db = FAISS.from_documents(chunks, embeddings)

    # Save the database so we can use it later
    db.save_local(index_path)
    print(f" Saved Aquatech index to folder: {index_path}")

    




