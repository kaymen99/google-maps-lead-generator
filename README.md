# **Google Maps Lead Generation: Find Business data Using AI**

This **AI lead generation tool** helps you discover and enrich local businesses data from any location. It combines the power of **Serper Maps API** with intelligent **AI web scraping** to build comprehensive business prospect lists that are ready for your sales outreach campaigns!

## **Why This Tool?**

- **Cost-Efficient** – Generate lead lists at the fraction of the cost of other scrapers
- **Fully Automated** – Handles the entire process from location search to lead enrichment
- **Contact Detail Extraction** – Automatically finds emails, social media profiles, and more
- **Smart Web Scraping** – Uses AI to navigate websites and extract relevant information
- **Ready-to-Use Output** – Generates Excel files you can immediately use for outreach
- **Multi-LLM Integration** – Choose any AI models like GPT-4.1, Claude or DeepSeek to run you search

## **How It Works**

The tool workflow is simple:

### 1. Data Collection
- Takes a location and search query input (e.g., "Toronto", "Realtors")
- Uses **Serper Maps API** to scrape Google Maps places data
- Returns a list of relevant places with basic information (business name, address, website, phone, etc.)

### 2. Data Enrichment
- For each business found, the tool scrapes their website (landing or contact pages)
- Uses an **AI agent (LLM)** to intelligently identify:
  - Email addresses
  - Detailed contact information
  - Social media links (Facebook, Twitter, Instagram, etc)
  - Other relevant data points for outreach

### 3. Data Export
- Saves all collected and enriched data to an Excel file, under the `data` directory
- Organizes information in a clean, ready-to-use format for sales outreach

## **Cost Implications**

While other Google Maps scrapers like [Apify's Google Maps Extractor](https://apify.com/compass/google-maps-extractor) or [Crawler Google Places](https://apify.com/compass/crawler-google-places) charge **$5-10 per 1000 results** (depending on the options you choose), this system leverages the Serper API and efficient web scraping to deliver the same results for approximately **$0.2 per 1000 leads** – that's up to **50x cheaper**!

Even better, Serper API offers **free credits** when you sign up, making your initial lead generation campaigns essentially **free**!

## 🛠️ **Project Structure**

```
.
├── main.py                # Main application script
├── process_from_excel.py  # Script to process existing Excel files
├── src/
│   ├── places_api.py      # Serper Maps API integration
│   ├── web_scraper.py     # Web scraping utilities with Playwright
│   ├── business_info.py   # Contact extraction and business data enrichment
│   ├── data_export.py     # Excel export functions
│   └── utils.py           # Utility functions
├── data/                  # Output folder for generated Excel files
└── requirements.txt       # Python dependencies
```

## **How to Use**

### Prerequisites

- Python 3.8+ installed
- Serper API key ([Get one here](https://serper.dev/))
- [OpenRouter API key](https://openrouter.ai/) (to use any LLM model) or you preferred LLM API key, like OpenAI or Claude

### Setup

Clone the repository and install dependencies:

```bash
# Clone the repository
git clone https://github.com/kaymen99/google-maps-lead-generator
cd google-maps-lead-generator

# Install dependencies
pip install -r requirements.txt
```

### Set up your API keys

Create a `.env` file in the root directory of the project and add your API keys:

```bash
SERPER_API_KEY=your-serper-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
```

### Running the Tool

Edit the parameters directly in `main.py` to customize your search:

```python
# In main.py
location = "Toronto"       # Location to search into
search_query = "Realtors" # Local business to search for
num_pages = 1             # Each page contains 20 results
```

Then you can run the tool with:

```bash
# Simply run the main.py file
python main.py
```

### 📊 **Output Files**

The tool automatically generates an Excel file in the `/data` directory at the root of your project:

- `data_[Query]_[Location]_[Date].xlsx`: Complete enriched business data including:
  - Business names and addresses
  - Phone numbers
  - Website URLs
  - **Extracted email addresses**
  - **Social media profiles** (Facebook, Twitter, Instagram)
  - **Contact information**
  - Additional business metadata (if you want to add more data like products, services, etc.)

This file is ready to use for your outreach campaigns with all the necessary contact details in one place!

## **Contributing**

Contributions are welcome! Please open an issue or submit a pull request for any changes. 

## **Contact**

If you have any questions or suggestions, feel free to reach out!
