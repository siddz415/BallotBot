import os
import PyPDF2


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
    return text


def process_pdfs_in_folder(folder_path):
    extracted_text = ''
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                print(f"Processing: {pdf_path}")
                extracted_text += extract_text_from_pdf(pdf_path) + '\n\n'
    return extracted_text


# Path to the data folder
data_folder = 'data'

# Extract text from all PDFs in the data folder and its subfolders
all_text = process_pdfs_in_folder(data_folder)

# Write the extracted text to a single file
output_file = 'all_pdf_text.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(all_text)


print(f"All PDF text has been extracted and saved to {output_file}")