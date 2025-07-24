# Prompts for AI-based operations

RESUME_PARSING_PROMPT = (
    "Extract programming skills from this resume: {resume_content}. "
    "Return them as a list of format ['skill1', 'skill2', ...]. "
    "Do not add any other text aside from the list of skills."
)

EXTERNAL_ENRICHMENT_PROMPT = (
    "Extract profile links from this candidate profile: {enrichment_request}. "
    "If no links are found, create profile links from this candidate profile."
    "Return them as a list of format ['link1', 'link2', ...]. "
    "Do not add any other text aside from the list of links."
)
