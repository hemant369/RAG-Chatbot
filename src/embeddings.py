from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings_models():
   
   print("Loading HuggingFace Embeddings model...")
   embeddings_models = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
   print("HuggingFace Embeddings model loaded.")

   return embeddings_models