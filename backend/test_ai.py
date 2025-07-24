from src.ai.groq import generate_chat_completion
from redis import Redis
from src.candidates.service import enqueue_resume_parsing, enqueue_external_enrichment

# Initialize Redis client
redis_client = Redis()

# Define a test payload
payload = {
    "content": "What is the meaning of life?"
}

# Test resume parsing
resume_payload = {"resume_content": "John Doe has experience in Python, FastAPI, and Redis."}
resume_task_id = enqueue_resume_parsing(redis_client, resume_payload)
print("Resume Parsing Task ID:", resume_task_id)

# Test external enrichment
enrichment_payload = {"enrichment_request": "John Doe's profile with LinkedIn and GitHub links."}
enrichment_task_id = enqueue_external_enrichment(redis_client, enrichment_payload)
print("Enrichment Task ID:", enrichment_task_id)