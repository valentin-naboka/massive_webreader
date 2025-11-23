# Massive LlamaIndex Web Loader

Implements WebLoader using Massive proxy network. This project integrates **LlamaIndex** and **Playwright** to load web content via residential proxies, enabling reliable data extraction across different regions. It features a custom `MassiveWebReader` that automatically handles proxy routing and browser fingerprinting (locale, timezone) based on the target country. A demo script is included to show how to fetch and summarize data using OpenAI.

## Contents

- **`massive_loader.py`**: The custom web loader that integrates Playwright with Massive proxies.
- **`demo_massive_loader.py`**: A demo script showing how to use the loader to fetch data from multiple countries.

## Features

- **Multi-Country Support**: Automatically routes traffic through residential proxies in the target country.
- **Browser Fingerprinting**: Dynamically adjusts browser locale, timezone, and headers to match the target region.

## Setup

1.  **Install Dependencies**:
    The `requirements.txt` includes the `playwright` Python library.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Browsers**:
    After installing the library, you must download the browser binaries:
    ```bash
    playwright install
    ```

3.  **Configure Environment**:
    Create a `.env` file with your credentials:
    ```env
    OPENAI_API_KEY=sk-...
    PROXY_USERNAME=your_massive_username
    PROXY_PASSWORD=your_massive_password
    ```

## Usage

Run the demo script:

```bash
python demo_massive_loader.py
```

Results will be saved to `iphone17_prices.json`.
