import os
from typing import List, Dict, TypedDict
from tqdm.asyncio import tqdm
from .data_export import update_business_data, load_excel_data
from .web_scraper import (
    scrape_website, extract_emails_from_content, 
    find_relevant_links
)
from .utils import ainvoke_llm


# Type definitions for structured data
class BusinessInfo(TypedDict):
    """TypedDict defining the structure of business information response"""
    facebook: str # Facebook link
    twitter: str # Twitter link
    instagram: str # Instagram link
    contact: str # Contact page link

class EmailsResponse(TypedDict):
    """TypedDict for email response"""
    emails: List[str]

async def analyze_business_links(
    links_dict: Dict[str, List[str]], 
    business_name: str, 
    business_location: str, 
    business_url: str
):
        # Create system prompt for the AI
    system_prompt = f"""
You are an expert at identifying the correct business information from scraped web data.
Your task is to analyze potential social media links for a business,
and determine which ones are most likely the official ones.

## Business Information
- Business Name: {business_name}
- Business Location: {business_location}
- Business Website URL: {business_url}

Provide only the most probable link for each category.
If no valid option exists for a category, return an empty string.
"""

    # Create user message with all the context
    user_message = f"""
    Potential Facebook links: {links_dict.get('facebook', [])}
    Potential Twitter links: {links_dict.get('twitter', [])}
    Potential Instagram links: {links_dict.get('instagram', [])}
    Potential Contact page links: {links_dict.get('contact', [])}
    """
    
    # Invoke LLM to get structured response
    response = await ainvoke_llm(
        model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        system_prompt=system_prompt,
        user_message=user_message,
        response_format=BusinessInfo,
        temperature=0.1
    )
    
    return response

async def analyze_business_emails(
    emails: List[str], 
    business_name: str, 
    business_location: str, 
    business_url: str
):
    system_prompt = f"""
Identify all relevant business contact emails. Prioritize general contact addresses (such as info@ or contact@) and emails of key personnel that use the business's domain. Exclude department-specific ones (e.g., press, events) unless no main contact is available.

If no domain-based business emails are found, provide any available emails, including personal or free-domain addresses (e.g., Gmail, Yahoo) as fallback contacts.

## Business Information
- Business Name: {business_name}
- Business Location: {business_location}
- Business Website URL: {business_url}

**If only a single valid email is found, just return it.**
"""

    # Create user message with all the context
    user_message = f"Potential emails: {list(emails)}"
    
    # Invoke LLM to get structured response
    response = await ainvoke_llm(
        model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        system_prompt=system_prompt,
        user_message=user_message,
        response_format=EmailsResponse,
        temperature=0.1
    )
    
    return response

async def get_business_info(
    business_url: str,
    business_name: str,
    business_location: str
):
    """
    Get comprehensive business information by scraping the website and analyzing the data.
    
    Args:
        business_url (str): URL of the business website
        business_name (str): Name of the business
        business_location (str): Location of the business
        
    Returns:
        Dict[str, str]: Business info with social media links and email
    """
    # Scrape the main website
    content, links = await scrape_website(business_url, extract_links=True)
    if not content:
        return {}
    social_links = find_relevant_links(links)
    emails = extract_emails_from_content(content)
    
    # Analyze the identified links
    links_result = await analyze_business_links(
        social_links, business_name, business_location, business_url
    )
    
    if emails:
        emails_result = await analyze_business_emails(
            emails, business_name, business_location, business_url
        )
    else:
        emails_result = {'emails': ''}

    # If no email found and we have a contact link, try scraping the contact page
    if (not emails_result.get('emails')) and social_links.get('contact'):
        contact_url = social_links['contact'][0]  # Take the first contact link
        if contact_url != business_url:
            contact_content, _ = await scrape_website(contact_url, extract_links=False)
            contact_emails = extract_emails_from_content(contact_content)
            if contact_emails:
                # Re-analyze with new emails
                emails_result = await analyze_business_emails(
                    contact_emails, business_name, business_location, business_url
                )

    # Return combined information
    return {
        'facebook': links_result.get('facebook', ''),
        'twitter': links_result.get('twitter', ''),
        'instagram': links_result.get('instagram', ''),
        'contact': links_result.get('contact', ''),
        'email': " || ".join(emails_result.get('emails', '')),
    }

async def process_businesses(excel_file, progress_callback=None) :
    """
    Process a list of businesses to extract detailed information and update the Excel file.
    
    Args:
        excel_file (str): Path to the Excel file to update
        
    Returns:
        List[Dict]: Enhanced business data with extracted information
    """
    # Load the Excel file into a DataFrame
    df, file_path = load_excel_data(excel_file)
    
    # Process each business with a progress bar
    for index, row in tqdm(df.iterrows(), desc="Processing businesses", unit="business"):
        name = row.get("name", "")
        url = row.get("website", "")
        location = row.get("address", "")
        already_searched = row.get("searched", "")
        
        if not url or already_searched == "YES":
            continue
        
        try:
            # Update UI progress via callback if provided
            if progress_callback and callable(progress_callback):
                await progress_callback(len(df), index, name)
                
            # Get business info
            info = await get_business_info(url, name, location)
            
            # Update the business information
            update_business_data(df, index, info)
        except Exception as e:
            print(f"Error processing {name}: {e}")
    
    # Save the updated DataFrame back to Excel
    try:
        df.to_excel(file_path, index=False)
    except Exception as e:
        print(f"Error saving Excel file: {e}")
