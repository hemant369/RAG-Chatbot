import ollama

def generate_response(query):
    response = ollama.chat(
        model="qwen2.5:3b", 
        messages=[
            {
                "role": "user", 
                "content": query
            }
        ],
        options={
            "num_predict": 512
        },
        keep_alive="30m"   # keeps model loaded for 30 minute
    )
    return response['message']['content']