import os
import json
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
    
    # Configure proxy credentials
    creds = None
    if os.getenv("PROXY_USERNAME") and os.getenv("PROXY_PASSWORD"):
        creds = {
            "username": os.getenv("PROXY_USERNAME"),
            "password": os.getenv("PROXY_PASSWORD"),
        }
        print("Proxy credentials found in environment.")

    # List of countries to scrape
    countries = ["DE", "US", "CA", "IT", "ES", "PL", "CZ"]
    results = {}

    for country in countries:
        print(f"\n--- Processing {country} ---")
        
        # Pass country parameter to the loader
        # The loader will handle locale, timezone, and proxy username modification
        params = {"country": country}
        
        try:
            print(f"Fetching content from {url}...")
            loader = MassiveWebReader(headless=True, creds=creds, params=params)
            documents = loader.load_data([url])
            
            print(f"Creating index for {country}...")
            index = SummaryIndex.from_documents(documents)
            query_engine = index.as_query_engine()
            
            print(f"Extracting data for {country}...")
            response = query_engine.query(
                """ Extract all iPhone 17 prices from the text below and return them in valid JSON.
                    If not price is available, return 'N/A'.
                    Example:
                    {
                        "model_name" : ["price1", "price2", "price3"],
                        "model_name2" : ["price1", "price2", "price3"],
                    }
                """)
            
            # Parse the response string into a JSON object
            try:
                response_text = str(response)
                # Simple heuristic to extract JSON block
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    results[country] = json.loads(json_str)
                else:
                    results[country] = response_text
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON for {country}")
                results[country] = str(response)
            
        except Exception as e:
            print(f"An error occurred for {country}: {e}")
            results[country] = f"Error: {e}"

    # Print final results
    print("\n--- Final Aggregated Results ---\n")
    print(json.dumps(results, indent=4, ensure_ascii=False))
    
    # Save to file
    output_file = "iphone17_prices.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
