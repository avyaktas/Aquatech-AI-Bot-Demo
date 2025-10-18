# to save query logs
import json
from datetime import datetime

import os
# load .emv file which contains API key
from dotenv import load_dotenv 
# Search through FAISS memory through langchain
from langchain_community.vectorstores import FAISS
# To covert text to vector using OpenAI embedding
from langchain_community.embeddings import OpenAIEmbeddings
# LLM engine
from langchain_community.chat_models import ChatOpenAI
# workflow, question -> FAISS -> GPT -> answer
from langchain.chains import RetrievalQA
# RAG Pattern ^^^
# For remembering memory
from langchain.chains import ConversationalRetrievalChain
# for merging retrievers
from langchain.retrievers import MergerRetriever
# openai import
load_dotenv()
from langchain.prompts import ChatPromptTemplate
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Prompt:
system_prompt = """
You are Aquatech’s internal assistant.

Style:
- Friendly, concise, and conversational.

Behavior:
- If the user greets/thanks/says bye (e.g., "hi", "hello", "thanks"), reply naturally and briefly (e.g., "Hi! How can I help?").
- Use provided document context when it’s relevant, but don’t refuse just because context is missing.
- If a question isn’t about company docs (general or small talk), answer from general knowledge.
- If the question is Aquatech-specific and you found no useful context, say you didn’t find a matching doc and give a short general answer if you can.
- Please include the source you are receiving the information from in the response in parenthesis. 
- Dont be consice, give all of the relvant information you can find unless asked to be consice. 

Examples:
User: hi
Assistant: Hi! How can I help today?

User: thanks
Assistant: You got it!
"""

# Step 1
# Take the saved FAISS db and load vector dbs
def loadSources(): 
    sources = [  #all the indexes you ca put you canadd as they are made
        "faiss_index_aquatech",
        "faiss_index"
    ]

    retrievers = []
    for path in sources: 
        print(f"🔍 Loading index: {path}")
        db = FAISS.load_local(
            path, 
            OpenAIEmbeddings(), 
            allow_dangerous_deserialization=True
        )
        retrievers.append(
            db.as_retriever(search_kwargs={"k": 6})  # fetch top 6 most relevant chunks
        )
    # merge all retrievers
    merged = MergerRetriever(retrievers = retrievers)
    return merged



# Step 2
# Retriever which searched documents
merged = loadSources()

# Step 3
# Connecting it together (retriever -> GPT)
# Ask questions -> Finds relevant chunks -> GPT -> answer
aqua_llm = ChatOpenAI(model = "gpt-3.5-turbo") # The model you are using
# RetrievalQA automates using retriever and llm

# Step 4
# Conversational RAG cgain
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human",
     "Use the context to answer the question.\n\n"
     "Context:\n{context}\n\n"
     "Question: {question}\n\n"
     "If the context does not contain the answer, say you don’t know.")
])
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=aqua_llm,
    retriever=merged,
    # this injects your qa_prompt into the “combine documents” step
    combine_docs_chain_kwargs={"prompt": qa_prompt},
    return_source_documents=True
)

# Step 5
# Takes user question and uses gpt to expand that question so RAG model has more context to work with and provide better output
def expandedQuery(user_query): 
    prompt = (
        "You are helping expand a user’s search for document retrieval.\n"
        "Return ONLY a short comma-separated list of useful related terms and synonyms "
        "that would help find the answer in company documents. No sentences.\n"
        f"Original question: {user_query}"
    )

    try:
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",   # model
            messages = [{"role": "user", "content": prompt}],   # tells model what user said
            temperature = 0.3   # model creativity
        )

        expanded_Query = response.choices[0].message.content
        return expanded_Query.strip()
    except Exception as e:
        print(f"[expand error] {e}")
        return user_query
    

# Step 6
# Talk to the AI

    
def runQuery(user_input, chat_history):
    expanded = expandedQuery(user_input)
    print(f"(Expanded query: {expanded})")

    # ask w memory
    response = qa_chain({
        "question": user_input,  
        "chat_history": chat_history,
    })
    
    answer = response["answer"]

    # save memory
    chat_history.append((expanded, answer))
    
    # log the query
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": user_input,
        "expanded_query": expanded,
        "answer": answer
    }
    os.makedirs("logs", exist_ok=True)
    with open("logs/query_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    
    return answer
    
    #If you want to quit
    
if __name__ == "__main__":
    print("Ask me anything about your documents (type 'exit' to quit)\n")
    chat_history = []
    while True:
        user_input = input("Your question: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        answer = runQuery(user_input, chat_history)
        print(answer)

  



    

