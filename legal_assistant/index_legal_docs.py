import openai
import faiss
import numpy as np
from django.conf import settings
from .models import LegalDocument
from langchain_community.embeddings import OpenAIEmbeddings


# Load API key from settings
openai.api_key = settings.OPENAI_API_KEY

# Initialize OpenAI Embeddings
embed_model = OpenAIEmbeddings()

# Function to create embeddings and store in FAISS
def index_legal_documents():
    documents = LegalDocument.objects.all()
    
    if not documents:
        print("No documents found!")
        return

    texts = [doc.content for doc in documents]
    
    # Generate embeddings
    embeddings = embed_model.embed_documents(texts)
    embeddings = np.array(embeddings).astype("float32")

    # Store in FAISS
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, "legal_doc_index.faiss")
    print("Legal documents indexed successfully!")

if __name__ == "__main__":
    index_legal_documents()
