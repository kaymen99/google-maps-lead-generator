import re
import html2text
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.async_api import async_playwright

# Precompiled email pattern for efficiency
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

async def scrape_website(url: str, extract_links: bool = False):
    """
    Scrape the given URL using Playwright. If the page contains an iframe, follow its src and scrape that instead.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--disable-http2"])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                locale="en-US",
                ignore_https_errors=True,
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.google.com/"
                }
            )

            page = await context.new_page()
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")

            html_content = await page.content()

            extracted_links = []
            if extract_links:
                extracted_links = extract_links_from_html(html_content, page.url)  # make sure this is defined
                
            # Convert HTML to markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            h.ignore_tables = True
            markdown_content = h.handle(html_content)
            markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content).strip()

            return markdown_content, extracted_links
    except Exception as e:
        print(f"Error scraping website: {e}")
        return None, []
    
def extract_links_from_html(html_content: str, main_url: str = ""):
    """
    Extract all unique links (hrefs) from HTML content.
    If a link is relative, prepend main_url using urljoin.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if href:
            # Accept only HTTP/HTTPS links as absolute
            if href.lower().startswith('http://') or href.lower().startswith('https://'):
                links.add(href)
            else:
                # Prepend main_url for all other relative links
                full_url = urljoin(main_url, href)
                links.add(full_url)
    return list(links)

def find_relevant_links(urls: list[str]):
    """
    Extracts social media and contact-related links from a list of URLs.
    """
    patterns = {
        "youtube": re.compile(r"^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/", re.I),
        "twitter": re.compile(r"^(https?:\/\/)?(www\.)?(twitter\.com|x\.com)\/", re.I),
        "facebook": re.compile(r"^(https?:\/\/)?(www\.)?facebook\.com\/", re.I),
        "instagram": re.compile(r"^(https?:\/\/)?(www\.)?instagram\.com\/", re.I),
        "linkedin": re.compile(r"^(https?:\/\/)?([a-z]{2,3}\.)?linkedin\.com\/", re.I),
        "contact": re.compile(r"contact", re.I)
    }

    result = {key: [] for key in patterns}

    for url in urls:
        for key, pattern in patterns.items():
            # For social patterns, use match (they should start with the platform)
            if key != "contact" and pattern.match(url):
                result[key].append(url)
            # For contact, use search (contact can appear anywhere in the URL)
            elif key == "contact" and pattern.search(url):
                result[key].append(url)
    return result

def extract_emails_from_content(content: str):
    """
    Extracts email addresses from content.
    """
    emails = set(email.lower() for email in EMAIL_PATTERN.findall(content))
    return list(emails)