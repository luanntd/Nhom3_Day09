import chromadb
import os
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path='./chroma_db')
try:
    client.delete_collection('day09_docs')
except:
    pass

col = client.get_or_create_collection('day09_docs', metadata={"hnsw:space": "cosine"})
model = SentenceTransformer('all-MiniLM-L6-v2')

docs_dir = './data/docs'
docs = []
metadatas = []
ids = []

for idx, fname in enumerate(os.listdir(docs_dir)):
    if not fname.endswith('.txt'): continue
    with open(os.path.join(docs_dir, fname), encoding='utf-8') as f:
        content = f.read()
    
    # Simple chunking by paragraph or just full doc for now
    chunks = [c.strip() for c in content.split('\n\n') if c.strip()]
    
    for c_idx, chunk in enumerate(chunks):
        docs.append(chunk)
        metadatas.append({"source": fname})
        ids.append(f"{fname}_chunk_{c_idx}")

embeddings = model.encode(docs).tolist()
col.add(
    documents=docs,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)
print(f"Index ready with {len(docs)} chunks.")
