import os
import json
import re
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from massive_reader import MassiveWebReader

def extract_valid_json(text):
    """Extract and clean JSON from an LLM response safely."""
    text = re.sub(r"```[a-zA-Z]*", "", text).replace("```", "").strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    matches = re.findall(r"\{.*\}", text, flags=re.DOTALL)
    if not matches:
        return None

    candidate = matches[-1]

    try:
        candidate = candidate.encode().decode("unicode_escape")
    except Exception:
        pass

    try:
        return json.loads(candidate)
    except Exception:
        return None

def extract_price_list(text):
    price_pattern = r"\b\d[\d\s]{0,15}\d(?:[.,]\d{2})?\s*(?:Kč|US\$|€|zł)?"
    prices = re.findall(price_pattern, text)
    clean = list({p.strip() for p in prices})
    return clean

def main():
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY missing.")
        return

    url = "https://www.google.com/search?q=iphone+17+price"

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
        max_attempts = 12
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

            try:
                documents = reader.load_data([url])
            except Exception as e:
                print(f"Scrape error: {e}")
                continue

            if not documents:
                print("No content — retrying.")
                continue

            text_len = len(documents[0].text)
            print(f"Length: {text_len}")

            if text_len >= 6000:
                break

            print("Too short — retrying...")

        if not documents:
            results[country] = {"error": "No data extracted"}
            continue

        # Clean, normalize text
        raw_text = re.sub(r"\s+", " ", documents[0].text)

        # Extract ALL prices for safety restrictions
        valid_prices = extract_price_list(raw_text)
        print(f"Detected {len(valid_prices)} price-like patterns.")

        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()

        prompt_template = f"""
You MUST return ONLY valid JSON. No comments, no explanations, no text outside JSON.

Below is a list of ALL valid prices detected in the text.  
You MUST choose prices ONLY from this whitelist:

VALID_PRICE_LIST = {valid_prices}

TASK:
Extract iPhone 17 model names AND the prices that belong to them.

==================================================
MODEL–PRICE ASSOCIATION RULE
==================================================
A price belongs to a model if it appears:
- in the same paragraph, OR
- within 250 characters before or after the model name.

==================================================
VALID MODEL NAMES
==================================================
Accept ONLY model names that appear EXACTLY in the text:
- iPhone 17
- iPhone 17 Pro
- iPhone 17 Pro Max
- iPhone 17 Air
- ANY other variant starting with "iPhone 17" exactly as written.

==================================================
PRICE RULES
==================================================
A valid price MUST:
- be in VALID_PRICE_LIST
- NOT be approximate (~) or ranges (x–y)
- NOT be speculative
- NOT be rental or monthly payment
- NOT be a placeholder or invented number

==================================================
FAILURE RULE
==================================================
If NO valid pairs exist, return EXACTLY: {{}}

==================================================
OUTPUT FORMAT
==================================================
Return ONLY JSON like:

{{
  "iPhone 17": ["price1", "price2"],
  "iPhone 17 Pro": ["price1"]
}}
"""

        response = query_engine.query(prompt_template)
        parsed = extract_valid_json(str(response))

        if parsed is None:
            print(f"⚠ Could not parse JSON for {country}")
            results[country] = {"error": "invalid_json", "raw": str(response)}
        else:
            results[country] = parsed
    print("\n--- Final Aggregated Results ---\n")
    print(json.dumps(results, indent=4, ensure_ascii=False))

    with open("iphone17_prices.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("\nSaved to iphone17_prices.json")

if __name__ == "__main__":
    main()