import os
import glob
import torch
import argparse
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# --- DYNAMIC PATH CONFIGURATION ---
# Get the absolute path of the directory where the script is located (e.g., /.../src)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory 
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# -------------------------------------------

# --- CLI ARGUMENTS ---
parser = argparse.ArgumentParser(description="Create a FAISS vector store with different chunking strategies.")

parser.add_argument('--strategy', type=str, required=True, choices=['size', 'markdown'],
                    help="The chunking strategy to use ('size' or 'markdown').")
parser.add_argument('--data_path', type=str, 
                    default=os.path.join(PROJECT_ROOT, 'data'), 
                    help="Path to the input data directory.")
parser.add_argument('--chunk_size', type=int, default=1024, help="Max chunk size for splitting.")
parser.add_argument('--chunk_overlap', type=int, default=100, help="Overlap between chunks.")

args = parser.parse_args()

# --- DYNAMIC CONFIGURATION ---
DATA_PATH = args.data_path

if args.strategy == 'markdown':
    output_folder_name = 'norm_md_vector_store'
else:  # This covers the 'size' strategy
    output_folder_name = 'norm_size_vector_store'

DB_FAISS_PATH = os.path.join(PROJECT_ROOT, output_folder_name)

# --------------------------------------------------------------------------------
EMBEDDING_MODEL_NAME = 'NeuML/pubmedbert-base-embeddings'
CHUNK_SIZE = args.chunk_size
CHUNK_OVERLAP = args.chunk_overlap

# --- HELPER FUNCTIONS FOR EACH STRATEGY ---

def get_chunks_by_size(data_path, chunk_size, chunk_overlap):
    """Strategy 1: Loads and splits documents by size."""
    print("Strategy: Splitting by size.")
    loader = DirectoryLoader(data_path, glob='**/*.md', show_progress=True, loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(documents)

def get_chunks_by_markdown(data_path, chunk_size, chunk_overlap):
    """Strategy 2: Splits documents first by markdown headers, then by size."""
    print("Strategy: Splitting by markdown headers (semantic).")
    md_files = glob.glob(os.path.join(data_path, '**', '*.md'), recursive=True)
    documents = []
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            documents.append(Document(page_content=f.read(), metadata={'source': filepath}))
            
    headers_to_split_on = [("##", "header"), ("###", "subheader"), ("####", "subsubheader")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    
    header_chunks = []
    for doc in documents:
        chunks = markdown_splitter.split_text(doc.page_content)
        for chunk in chunks:
            chunk.metadata['source'] = doc.metadata['source']
        header_chunks.extend(chunks)

    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
        )
    
    final_chunks = []
    for chunk in header_chunks:
        if len(chunk.page_content) > chunk_size:
            sub_chunks = size_splitter.split_documents([chunk])
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(chunk)
    return final_chunks

# --- MAIN WORKFLOW ---
def main():
    print(f"Starting vector store creation with '{args.strategy}' strategy.")
    print(f"Output will be saved to '{DB_FAISS_PATH}'.")

    # 1. Choose chunking strategy based on the argument
    if args.strategy == 'size':
        chunks = get_chunks_by_size(DATA_PATH, CHUNK_SIZE, CHUNK_OVERLAP)
    else: # 'markdown'
        chunks = get_chunks_by_markdown(DATA_PATH, CHUNK_SIZE, CHUNK_OVERLAP)
    
    if not chunks:
        print(f"Error: No text chunks were created. Check the data path '{DATA_PATH}'.")
        return
    print(f"Created {len(chunks)} text chunks.")

    # 2. Add source filename to metadata (common to both strategies)
    for chunk in chunks:
        source_path = chunk.metadata.get('source', 'Unknown')
        chunk.metadata['filename'] = os.path.basename(source_path)

    # 3. Create embeddings and vector store (common to both strategies)
    print("Creating embeddings and building FAISS vector store...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True}
    )
    db = FAISS.from_documents(chunks, embeddings)
    
    # 4. Save the store
    db.save_local(DB_FAISS_PATH)
    print(f"\n--- Success! ---")
    print(f"Vector store created and saved to '{DB_FAISS_PATH}'")

if __name__ == "__main__":
    main()