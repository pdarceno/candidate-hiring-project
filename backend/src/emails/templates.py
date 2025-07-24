# Email templates for candidate tasks
def generate_resume_email(candidate_id: str, skills: list) -> str:
    """Generate the HTML content for the resume email."""
    skills_content = '<br>'.join(skills) if skills else 'No skills found'
    return (
        f"<p>Good day,</p>"
        f"<p>Please see attached skills for candidate {candidate_id} for your review:</p>"
        f"<p>{skills_content}</p>"
        f"<p>Kind Regards,</p>"
    )


def generate_enhancement_email(candidate_id: str, profile_links: list) -> str:
    """Generate the HTML content for the enhancement email."""
    links_content = '<br>'.join(profile_links) if profile_links else 'No links found'
    return (
        f"<p>Good day,</p>"
        f"<p>Please see attached links for candidate {candidate_id} for your review:</p>"
        f"<p>{links_content}</p>"
        f"<p>Kind Regards,</p>"
    )
