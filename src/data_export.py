import os
import pandas as pd

def save_places_to_excel(places_data, filename):
    """
    Save places data to an Excel file in the 'data' folder.
    
    Args:
        places_data (List[Dict]): List of places data from the Serper Maps API
        filename (str): Name of the Excel file to save
    """
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Set the full file path
    file_path = os.path.join(data_dir, filename)
    
    # Extract places from all pages
    all_places = []
    for page_data in places_data:
        if 'places' in page_data:
            all_places.extend(page_data['places'])
    
    if not all_places:
        print("No places data to save.")
        return
    
    # Create DataFrame with relevant columns
    df = pd.DataFrame([{
        'name': place.get('title', ''),
        'address': place.get('address', ''),
        'website': place.get('website', '') or place.get('url', ''),
        'phone': place.get('phoneNumber', ''),
        'description': place.get('description', ''),
        'rating': place.get('rating', ''),
        'reviews': place.get('ratingCount', ''),
        'category': place.get('type', ''),
        'keywords': " || ".join(place.get('types', [])),
        'price_level': place.get('priceLevel', ''),
        'opening_hours': place.get('openingHours', {}),
        'email': '',
        'facebook': '',
        'twitter': '',
        'instagram': '',
        'searched': 'NO',
    } for place in all_places])
    
    # Save to Excel
    df.to_excel(file_path, index=False)
    print(f"Data saved to {file_path}")

def update_business_data(df, index, info):
    """
    Helper function to update a business's information in the Excel DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the businesses
        index: Row index to update
        info (Dict[str, Any]): Information to update (email, social media links)
    """
    # Update the row with the new information using the provided index
    if info:
        df.at[index, 'email'] = info.get('email', '')
        df.at[index, 'facebook'] = info.get('facebook', '')
        df.at[index, 'twitter'] = info.get('twitter', '')
        df.at[index, 'instagram'] = info.get('instagram', '')
    df.at[index, 'searched'] = "YES"

def load_excel_data(filename: str) -> pd.DataFrame:
    """
    Load places data from an Excel file.
    
    Args:
        filename (str): Name of the Excel file to load
        
    Returns:
        pd.DataFrame: DataFrame containing the places data
    """
    # Handle paths with or without data directory
    if not filename.startswith('data/'):
        file_path = os.path.join('data', filename)
    else:
        file_path = filename
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    # Load DataFrame from Excel
    df = pd.read_excel(file_path)
    
    # Filter out already searched data
    df = df[~(df.get('searched') == 'YES')]
    
    # Replace Nan with ""
    df = df.fillna("")
    
    return df, file_path