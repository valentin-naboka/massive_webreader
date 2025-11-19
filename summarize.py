import os
from dotenv import load_dotenv
from llama_index.core import SummaryIndex
from massive_loader import MassiveWebReader

# Load environment variables
load_dotenv()

def main():
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key.")
        return

    url = "https://www.google.com/search?q=iphone+17+price"
    print(f"Fetching content from {url}...")

    # Configure proxy if available
    proxy = None
    if os.getenv("PROXY_USERNAME") and os.getenv("PROXY_PASSWORD"):
        creds = {
            "username": os.getenv("PROXY_USERNAME"),
            "password": os.getenv("PROXY_PASSWORD"),
        }
        print(f"Using proxy")


    params = { "country" : "DE"}
    try:
        # Load data from the web page using Playwright
        loader = MassiveWebReader(headless=True, creds=creds, params=params)
        documents = loader.load_data([url])
        
        print("Creating index...")
        # Create a summary index
        index = SummaryIndex.from_documents(documents)
        
        # Create a query engine
        query_engine = index.as_query_engine()
        
        print("Extracting data...")
        # Ask for a summary
        response = query_engine.query(
            """ Extract iPhone 17 prices into JSON format:
                {
                    "model_name" : ["price1", "price2", "price3"],
                    "model_name2" : ["price1", "price2", "price3"],
                }
            """)
        
        print("\n--- Extracted Data ---\n")
        print(response)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
