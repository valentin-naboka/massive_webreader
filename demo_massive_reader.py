import os
import json
import re
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from massive_reader import MassiveWebReader

# Load environment variables
load_dotenv()

def extract_valid_json(text):
    """Extract and clean JSON from an LLM response safely."""
    # 1. Strip markdown fences
    text = re.sub(r"```[a-zA-Z]*", "", text).replace("```", "").strip()

    # 2. Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # 3. Extract JSON-like block
    matches = re.findall(r"\{.*\}", text, flags=re.DOTALL)
    if not matches:
        return None

    candidate = matches[-1]

    # 4. Unescape strings like "{\"a\": \"b\"}"
    try:
        candidate = candidate.encode().decode("unicode_escape")
    except Exception:
        pass

    # 5. Try parse again
    try:
        return json.loads(candidate)
    except Exception:
        return None

def main():
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found.")
        return

    url = "https://www.google.com/search?q=iphone+17+price"

    # Proxy credentials
    creds = None
    if os.getenv("PROXY_USERNAME") and os.getenv("PROXY_PASSWORD"):
        creds = {
            "username": os.getenv("PROXY_USERNAME"),
            "password": os.getenv("PROXY_PASSWORD"),
        }
        print("Proxy credentials found.")

    # List of countries to scrape
    countries = ["DE", "US", "CA", "IT", "ES", "PL", "CZ"]
    results = {}

    for country in countries:
        print(f"\n--- Processing {country} ---")
        params = {"country": country}

        try:
            print(f"Fetching content from {url}...")

            max_attempts = 6
            attempt = 0
            documents = []

            while attempt < max_attempts:
                attempt += 1
                print(f"Attempt {attempt}/{max_attempts}...")

                reader = MassiveWebReader(
                    headless=False,
                    creds=creds,
                    params=params
                )

                documents = reader.load_data([url])

                if not documents:
                    print("No documents returned — retrying.")
                    continue

                text_len = len(documents[0].text)
                print(f"Document length: {text_len}")

                if text_len >= 2000:
                    print("Content length OK — stopping retries.")
                    break

                print("Content too short — retrying...")

            index = VectorStoreIndex.from_documents(documents)
            query_engine = index.as_query_engine()

            print(f"Extracting JSON for {country}...")
            response = query_engine.query(
                """
                You MUST return ONLY valid JSON. No comments, no text outside JSON.

                TASK:
                Extract all iPhone 17 model names and their prices from the provided text.

                RULES:
                - Remove duplicates.
                - Remove invalid values: "0.00", "0.00", "0", "N/A".
                - Preserve local currency.
                - JSON structure:

                {
                  "model_name": ["price1", "price2"],
                  "model_name2": ["price1"]
                }

                Return ONLY JSON.
                """
            )

            response_text = str(response)
            parsed = extract_valid_json(response_text)

            if parsed is None:
                print(f"Warning: Could not parse JSON for {country}")
                results[country] = {"error": "invalid_json", "raw": response_text}
                continue

            results[country] = parsed

        except Exception as e:
            print(f"Error for {country}: {e}")
            results[country] = {"error": str(e)}

    print("\n--- Final Aggregated Results ---\n")
    print(json.dumps(results, indent=4, ensure_ascii=False))

    with open("iphone17_prices.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("\nSaved to iphone17_prices.json")


if __name__ == "__main__":
    main()