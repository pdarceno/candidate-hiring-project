"""
Utility functions for parsing AI responses safely
"""
import json
import re
import logging
from typing import List, Any, Union

logger = logging.getLogger(__name__)


def safe_parse_list_response(response: str, fallback_empty: bool = True) -> List[str]:
    """
    Safely parse AI response that should contain a list.
    
    Args:
        response: The raw response string from AI
        fallback_empty: If True, return empty list on parsing failure. 
                       If False, raise exception on parsing failure.
    
    Returns:
        List of strings extracted from the response
        
    Raises:
        ValueError: If parsing fails and fallback_empty is False
    """
    if not response or not isinstance(response, str):
        if fallback_empty:
            return []
        raise ValueError("Empty or invalid response")
    
    # Clean the response
    cleaned_response = response.strip()
    
    # Remove any extra text before/after the list
    list_match = re.search(r'\[.*\]', cleaned_response, re.DOTALL)
    if list_match:
        cleaned_response = list_match.group(0)
    
    # Try JSON parsing first
    try:
        # If it's a Python list format, convert to JSON format
        if cleaned_response.startswith('[') and cleaned_response.endswith(']'):
            # Replace single quotes with double quotes for JSON compatibility
            json_formatted = re.sub(r"'([^']*)'", r'"\1"', cleaned_response)
            parsed_list = json.loads(json_formatted)
            
            # Ensure all items are strings and clean them
            result = [str(item).strip() for item in parsed_list if item]
            return result
            
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing failed: {e}")
    
    # Fallback: try to extract items using regex
    try:
        # Extract items between quotes (single or double)
        items = re.findall(r'["\']([^"\']+)["\']', cleaned_response)
        if items:
            result = [item.strip() for item in items if item.strip()]
            logger.info(f"Used regex fallback, extracted {len(result)} items")
            return result
            
        # If no quoted items, try comma-separated values inside brackets
        bracket_content = re.search(r'\[(.*)\]', cleaned_response, re.DOTALL)
        if bracket_content:
            content = bracket_content.group(1)
            items = [item.strip().strip('\'"') for item in content.split(',')]
            result = [item for item in items if item]
            logger.info(f"Used bracket content parsing, extracted {len(result)} items")
            return result
            
    except Exception as e:
        logger.error(f"Regex parsing failed: {e}")
    
    # Final fallback
    if fallback_empty:
        logger.warning(f"Could not parse response, returning empty list: {response[:100]}...")
        return []
    else:
        raise ValueError(f"Could not parse list from response: {response[:100]}...")


def safe_parse_skills(response: str) -> List[str]:
    """
    Specifically parse programming skills from AI response.
    
    Args:
        response: Raw AI response containing skills
        
    Returns:
        List of programming skills
    """
    skills = safe_parse_list_response(response)
    
    # Additional cleaning for skills
    cleaned_skills = []
    for skill in skills:
        # Remove common prefixes/suffixes
        cleaned_skill = skill.strip()
        cleaned_skill = re.sub(r'^(programming\s+|language\s+|skill\s+)', '', cleaned_skill, flags=re.IGNORECASE)
        cleaned_skill = re.sub(r'\s+(programming|language|skill)$', '', cleaned_skill, flags=re.IGNORECASE)
        
        if cleaned_skill and len(cleaned_skill) > 1:  # Skip single characters
            cleaned_skills.append(cleaned_skill)
    
    return cleaned_skills


def safe_parse_links(response: str) -> dict[str, str]:
    """
    Specifically parse profile links from AI response.
    
    Args:
        response: Raw AI response containing links as JSON object
        
    Returns:
        Dictionary of profile links with platform names as keys
    """
    if not response or not isinstance(response, str):
        return {}
    
    # Clean the response
    cleaned_response = response.strip()
    
    # Try to find JSON object in response
    json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
    if json_match:
        cleaned_response = json_match.group(0)
    
    # Try JSON parsing
    try:
        parsed_links = json.loads(cleaned_response)
        if isinstance(parsed_links, dict):
            # Validate and clean URLs
            valid_links = {}
            for platform, url in parsed_links.items():
                url = str(url).strip()
                
                # Basic URL validation
                if url and ('http' in url.lower() or 'www.' in url.lower() or '.' in url):
                    # Add protocol if missing
                    if not url.startswith(('http://', 'https://')):
                        if url.startswith('www.'):
                            url = 'https://' + url
                        elif '.' in url and not url.startswith(('ftp://', 'mailto:')):
                            url = 'https://' + url
                    
                    valid_links[platform.strip()] = url
            
            return valid_links
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing failed for links: {e}")
    except Exception as e:
        logger.error(f"Error parsing links: {e}")
    
    # Return empty dict if parsing fails
    logger.warning(f"Could not parse links, returning empty dict: {response[:100]}...")
    return {}


def validate_parsing_result(result: List[str], expected_type: str = "items", min_items: int = 0, max_items: int = 100) -> bool:
    """
    Validate the parsing result.
    
    Args:
        result: The parsed list
        expected_type: Type of items for logging
        min_items: Minimum expected items
        max_items: Maximum expected items
        
    Returns:
        True if validation passes, False otherwise
    """
    if not isinstance(result, list):
        logger.error(f"Expected list but got {type(result)}")
        return False
    
    if len(result) < min_items:
        logger.warning(f"Got {len(result)} {expected_type}, expected at least {min_items}")
        return False
    
    if len(result) > max_items:
        logger.warning(f"Got {len(result)} {expected_type}, expected at most {max_items}")
        return False
    
    logger.info(f"Successfully parsed {len(result)} {expected_type}")
    return True