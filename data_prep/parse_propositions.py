import os
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import Document
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["propositions_db"]
collection = db["parsed_propositions"]


def parse_proposition(pdf_path):
    # Initialize LlamaParse
    llama_parse = LlamaParse(
        api_key=os.getenv("LLAMA_PARSE_API_KEY"),
        result_type="markdown"
    )

    # Parse the PDF
    parsed_doc = llama_parse.load_data(pdf_path)
# The parsed content is now in markdown format
    return parsed_doc[0].text  # Assuming there's only one document returned


def process_propositions(folder_path):
    parsed_propositions = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                print(f"Processing: {pdf_path}")
                parsed_content = parse_proposition(pdf_path)
                parsed_propositions[file] = parsed_content
                
                # Add to MongoDB
                document = {
                    "file_name": file,
                    "content": parsed_content
                }
                collection.insert_one(document)
                print(f"Added {file} to MongoDB")
    
    return parsed_propositions


# Path to the propositions folder
# propositions_folder = 'data/2024-11-CA propositions'
propositions_folder = 'data/2024-11-SF propositions'

# Parse all propositions in the folder and add to MongoDB
parsed_data = process_propositions(propositions_folder)

# Write the parsed data to a single file (optional, since we're using MongoDB)
output_file = 'parsed_propositions.md'
with open(output_file, 'w', encoding='utf-8') as file:
    for proposition, content in parsed_data.items():
        file.write(f"# Proposition: {proposition}\n\n")
        file.write(content)
        file.write("\n\n---\n\n")

print(f"All propositions have been parsed, saved to MongoDB, and optionally saved to {output_file}")

# Close the MongoDB connection
client.close()