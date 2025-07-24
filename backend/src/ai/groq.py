from groq import AsyncGroq
import os

async def generate_parser(content: str, model: str = "llama-3.3-70b-versatile", stream: bool = False) -> str:
    """Generate a parser  using the Groq API asynchronously."""
    client = AsyncGroq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = await client.chat.completions.create(
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