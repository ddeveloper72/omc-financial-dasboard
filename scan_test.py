"""Quick script to test document scanning"""
import os
from dotenv import load_dotenv
from utils.document_scanner import DocumentScanner

load_dotenv()

# Get document path
doc_path = os.getenv('DOCUMENT_SOURCE_PATH', r'C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM')
print(f"Scanning directory: {doc_path}")
print(f"Directory exists: {os.path.exists(doc_path)}")
print()

# Scan for documents
scanner = DocumentScanner(doc_path)
documents = scanner.scan_directory()

print(f"Found {len(documents)} documents")
print()

# Display all documents
print("=" * 120)
for i, doc in enumerate(documents, 1):
    print(f"{i:2}. Year: {doc['year'] or 'N/A':4} | {doc['filename']}")
print("=" * 120)
print(f"\nYears found: {sorted(set(doc['year'] for doc in documents if doc['year']))}")
