import os
from dotenv import load_dotenv
from pymongo import MongoClient
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
import cohere

# Load environment variables from .env file
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["propositions_db"]
source_collection = db["parsed_propositions"]
target_collection = db["processed_chunks"]

# Initialize Cohere client
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Initialize sentence splitter
node_parser = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=20
)

def process_and_embed_document(doc):
    file_name = doc['file_name']
    content = doc['content']
    
    # Create a Document object
    document = Document(text=content, metadata={"file_name": file_name})
    
    # Split the document into nodes
    nodes = node_parser.get_nodes_from_documents([document])
    
    # Process each node
    for i, node in enumerate(nodes):
        # Generate embedding using Cohere API directly
        response = co.embed(
            texts=[node.text],
            model='embed-english-v3.0',
            input_type='search_document'
        )
        embedding = response.embeddings[0]
        
        # Create a document for MongoDB
        chunk_doc = {
            "file_name": file_name,
            "chunk_index": i,
            "text": node.text,
            "embedding": embedding
        }
        
        # Insert into the new collection
        target_collection.insert_one(chunk_doc)
        
    print(f"Processed and embedded {len(nodes)} chunks for {file_name}")

# Process all documents
def process_all_documents():
    for doc in source_collection.find():
        process_and_embed_document(doc)

# Run the processing
process_all_documents()

print("All documents have been processed, split, embedded, and saved to the new MongoDB collection.")

# Close the MongoDB connection
client.close()