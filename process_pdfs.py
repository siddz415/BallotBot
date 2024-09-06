import os
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_parse import LlamaParse
from mongodb_setup import setup_mongodb

# Load environment variables
load_dotenv()

# LlamaParse configuration
llama_parse = LlamaParse(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))

