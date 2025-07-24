from groq import Groq
import os

def generate_chat_completion(content: str, model: str = "llama-3.3-70b-versatile", stream: bool = False) -> str:
    """Generate a chat completion using the Groq API."""
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY", "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"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        model=model,
        stream=stream,
    )

    return chat_completion.choices[0].message.content