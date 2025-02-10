from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from .models import LegalDocument


class KnowledgeBaseIndex:
    def __init__(self):
        self.embedding_function = OpenAIEmbeddings()

        # Initialize vector store (we'll build the index in the next step)
        self.vector_store = None

    def build_index(self):
        # Get all legal documents
        documents = LegalDocument.objects.all()

        # Generate embeddings for the documents' content
        document_texts = [doc.content for doc in documents]

        # Create embeddings for each document
        embeddings = self.embedding_function.embed_documents(document_texts)

        # Create a list of documents with their embeddings
        docs_for_faiss = [
            {
                "page_content": doc.content,
                "metadata": {"title": doc.title},
                "embedding": embedding
            }
            for doc, embedding in zip(documents, embeddings)
        ]
        
        # Rebuild the FAISS index using the embeddings
        self.vector_store = FAISS.from_documents(
            documents=docs_for_faiss,
            embedding=self.embedding_function
        )

    def query(self, query_text):
        # Get query embedding
        query_embedding = self.embedding_function.embed_query(query_text)

        # Perform similarity search in the vector store
        _, I = self.vector_store.similarity_search(query_embedding, k=3)

        # Get relevant documents
        relevant_docs = LegalDocument.objects.filter(id__in=I[0])
        context = "\n".join([doc.content for doc in relevant_docs])
        
        return {
            "query": query_text,
            "context": context,
            "relevant_documents": relevant_docs
        }

# Export the index instance
index = KnowledgeBaseIndex()
