def retrieve_documents(vectorstore, query):

   print("User Query:", query)
   
   documents = vectorstore.similarity_search(query, k=3)

   print(f"Retrieved {len(documents)} documents.")

   for index, doc in enumerate(documents):
       print(f"Document {index + 1}:")
       print(doc.page_content[:200])  # Print the first 200 characters of each document
       print("\n---\n")
   return documents