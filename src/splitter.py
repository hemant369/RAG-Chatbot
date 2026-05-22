from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text(text):

    print("Splitting text into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    chunks = splitter.create_documents([text])

    print("Text splitting completed.")
    return chunks