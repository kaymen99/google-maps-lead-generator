import streamlit as st
import asyncio
import os
import pandas as pd
from io import BytesIO
from src.places_api import search_places, get_coordinates
from src.business_info import process_businesses
from src.data_export import save_places_to_excel
from src.utils import get_current_date
from dotenv import load_dotenv

load_dotenv()

# Set page config
st.set_page_config(
    page_title="Google Maps Lead Generator",
    page_icon="🔍",
    layout="wide"
)

# App title and description
st.title("AI-Powered Google Maps Lead Generator")
st.markdown(
    """
    This tool helps you generate leads from Google Maps by:
    1. Searching for businesses matching your criteria
    2. Extracting contact information from their websites
    3. Using AI to find emails and social media profiles
    """
)

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # API Keys
    st.subheader("API Keys")
    serper_api_key = st.text_input("Serper API Key", type="password")
    openrouter_api_key = st.text_input("OpenRouter API Key", type="password")
    
    # LLM Model Settings
    st.subheader("LLM Model")
    llm_model = st.selectbox(
        "Select LLM Model",
        options=[
            "openai/gpt-4.1-mini",
            "openai/gpt-4o-mini",
            "anthropic/claude-3-haiku",
            "anthropic/claude-3.5-sonnet",
            "deepseek/deepseek-chat",
            "mistral/mistral-large-2"
        ],
        index=0,
    )
    
    # Save settings button
    if st.button("Save Settings"):
        # Temporarily set environment variables for this session
        os.environ["SERPER_API_KEY"] = serper_api_key
        os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
        os.environ["LLM_MODEL"] = llm_model
        st.success("Settings saved for this session!")

# Main form
with st.form("search_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        location = st.text_input("Location (city, address, etc.)", value="New York")
        search_query = st.text_input("Search Query (e.g., 'coffee shops', 'dentists')", value="Real Estate Agents")
    
    with col2:
        num_places = st.number_input("Number of Places to Scrape", min_value=20, max_value=1000, value=20, step=20)
        num_pages = max(1, num_places // 20)  # Calculate number of pages (20 results per page)
    
    submit_button = st.form_submit_button("Start Lead Generation")

# Initialize session state if not already done
if "excel_path" not in st.session_state:
    st.session_state.excel_path = None

async def main_with_progress(location, search_query, num_pages):
    """
    Main function with progress reporting for Streamlit
    """
    # Status placeholder for showing current operation
    status = st.empty()
    
    # Step 1: Get coordinates from location
    status.text("🔍 Getting coordinates for location...")
    coords = get_coordinates(location)
    if not coords:
        st.error("❌ Could not get coordinates for the location. Please check the location name and try again.")
        return None
        
    # Step 2: Search for places using Serper Maps API
    status.text("🔍 Searching for businesses using Serper Maps API...")
    places_data = search_places(search_query, coords, num_pages)
    if not places_data:
        st.error("❌ No places found. Try a different search query or location.")
        return None
        
    # Step 3: Save places data to Excel
    status.text("💾 Saving initial data to Excel...")
    excel_filename = f"data_{search_query}_{location}_{get_current_date()}.xlsx"
    
    # Make sure excel file is saved in the data directory
    file_path = save_places_to_excel(places_data, excel_filename)
    
    # Step 4: Process businesses to get detailed information
    status.text("🌐 Processing businesses to extract detailed information...")
    
    # Create a Streamlit progress bar
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    # Define a custom callback to track progress
    async def progress_callback(total, current, business_name):
        # Update the progress bar
        progress_bar.progress((current + 1) / total)
        progress_text.text(f"Processing: {current + 1}/{total} - {business_name}")
    
    # Process the businesses with our progress callback
    await process_businesses(file_path, progress_callback=progress_callback)
    
    status.text("✅ Lead generation complete!")
    
    return file_path


# Main execution logic
if submit_button:
    # Check if API keys are set
    if not os.environ.get("SERPER_API_KEY") or not os.environ.get("OPENROUTER_API_KEY"):
        st.error("⚠️ Please set your API keys in the sidebar before starting.")
    else:
        with st.spinner("Starting lead generation..."):
            # Run the async function
            excel_path = asyncio.run(main_with_progress(location, search_query, num_pages))
            if excel_path:
                st.session_state.excel_path = excel_path

# Download section - Always check if the file exists
if st.session_state.excel_path and os.path.exists(st.session_state.excel_path):
    st.subheader("Download Results")
    
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(st.session_state.excel_path)
        
        # Display a preview of the data
        if not df.empty:
            st.write(f"Found {len(df)} businesses:")
            st.dataframe(df)
            
            # Create a download button
            with open(st.session_state.excel_path, "rb") as excel_file:
                excel_bytes = excel_file.read()
                
            st.download_button(
                label="📥 Download Excel File",
                data=excel_bytes,
                file_name=os.path.basename(st.session_state.excel_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_button"
            )
    except Exception as e:
        st.error(f"Error displaying results: {e}")
        st.write(f"You can find your file at: {st.session_state.excel_path}")
        
