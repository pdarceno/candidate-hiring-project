# Prompts for AI-based operations

RESUME_PARSING_PROMPT = (
    "Extract programming skills from this resume: {resume_content}. "
    "Return them as a list of format ['skill1', 'skill2', ...]. "
    "Do not add any other text aside from the list of skills."
)

EXTERNAL_ENRICHMENT_PROMPT = (
    "Extract profile links from this candidate profile: {enrichment_request}. "
    "Return them as a JSON object with platform names as keys and URLs as values. "
    "Example: {{\"LinkedIn\": \"https://linkedin.com/in/username\", \"GitHub\": \"https://github.com/username\"}}. "
    "If no links are found, return an empty object {{}}. "
    "Do not add any other text aside from the JSON object."
)
