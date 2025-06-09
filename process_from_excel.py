import asyncio
from src.business_info import process_businesses
from dotenv import load_dotenv


load_dotenv()


if __name__ == "__main__":
    excel_file = "data_Solar Roofing_Barcelona_2025-06-09 12:50.xlsx"
    
    # Run the main function
    asyncio.run(process_businesses(excel_file))
