# Massive LlamaIndex Web Loader

Implements WebLoader using Massive proxy network. This project integrates **LlamaIndex** and **Playwright** to load web content via residential proxies, enabling reliable data extraction across different regions. It features a custom `MassiveWebReader` that automatically handles proxy routing and browser fingerprinting (locale, timezone) based on the target country. A demo script is included to show how to fetch and summarize data using OpenAI.

## Demo
<video src="https://private-user-images.githubusercontent.com/52565022/517900198-4795b2a7-4e32-4ab7-8dc1-f16121c4e689.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjM5Mzc5ODgsIm5iZiI6MTc2MzkzNzY4OCwicGF0aCI6Ii81MjU2NTAyMi81MTc5MDAxOTgtNDc5NWIyYTctNGUzMi00YWI3LThkYzEtZjE2MTIxYzRlNjg5Lm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTExMjMlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUxMTIzVDIyNDEyOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWQ4YWY0OTE1Njg4ZmIzYTJhNGUyOTdjMDJhMjI1N2YzODg3MjhmOWFiMDExYTg4YmZkOWYzNGViZmZmMDU2YjQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.YvzXbWplUn9fQyODv7a6U4gsx-tD1pMJY6Rea9KBOyc" controls></video>

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
