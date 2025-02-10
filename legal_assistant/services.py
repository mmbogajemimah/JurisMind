import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from .models import LegalDocument

class KnowledgeBaseService:
    def __init__(self):
        # Initialize the OpenAI embedding function
        self.embedding_function = OpenAIEmbeddings()

        # Initialize FAISS vector store (empty for now)
        self.vector_store = FAISS([], embedding_function=self.embedding_function)

    def build_index(self):
        # Retrieve all legal documents
        documents = LegalDocument.objects.all()

        # Create a list of document contents and metadata
        doc_contents = [doc.content for doc in documents]
        doc_metadata = [{"title": doc.title} for doc in documents]

        # Generate embeddings for the document contents
        embeddings = self.embedding_function.embed_documents(doc_contents)

        # Add documents to FAISS index
        self.vector_store.add_texts(
            texts=doc_contents,
            metadatas=doc_metadata,
            embeddings=embeddings
        )

    def query(self, query_text):
        # Get the embedding for the query
        query_embedding = self.embedding_function.embed_query(query_text)

        # Perform similarity search in the vector store
        search_results = self.vector_store.similarity_search(query_embedding, k=3)

        # Collect and return relevant documents
        context = "\n".join([result["text"] for result in search_results])
        return {
            "query": query_text,
            "context": context,
            "relevant_documents": search_results
        }

# Export the service instance
knowledge_base_service = KnowledgeBaseService()
