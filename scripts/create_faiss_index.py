import faiss
import numpy as np

# Define the dimensionality of your embeddings (e.g., 128, 512, 1536)
dimension = 128  # Change this according to your embeddings

# Create a FAISS index with L2 (Euclidean) distance
index = faiss.IndexFlatL2(dimension)

# Generate some random example embeddings
num_vectors = 5  # Number of documents
vectors = np.random.rand(num_vectors, dimension).astype("float32")

# Add vectors to the FAISS index
index.add(vectors)

# Save the FAISS index to a file
faiss.write_index(index, "legal_doc_index.faiss")

print("FAISS index created and saved as 'legal_doc_index.faiss'")
