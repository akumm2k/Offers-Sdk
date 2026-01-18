# Offers SDK

A modern, async-first Python SDK for fetching and managing product offers with token-based authentication, intelligent caching, and comprehensive error handling.

## CLI Demo

![demo gif](demo/demo.gif)

## Features

- **Async-First Design**: Full `async/await` support for non-blocking API calls
- **Automatic Token Management**: Handles access token refresh using refresh tokens, with JWT expiry detection
- **HTTP Client Flexibility**: Built-in `requests` client with easy extensibility for other HTTP libraries
- **Intelligent Caching**: HTTP response caching with configurable TTL (5 minutes default) to improve performance, with token redaction
- **Retry Logic**: Automatic retry with exponential backoff for transient failures
- **Secure Token Storage**: Persistent token storage using system keyring for secure credential management
- **Comprehensive Error Handling**: Domain exception types (`AuthenticationError`, `ValidationError`, `ServerError`) for better error context
- **Full Type Hints**: Complete type annotations throughout the codebase for IDE support and type checking
- **CLI Tool**: Interactive command-line interface for testing

## Description

The Offers SDK provides a Pythonic interface to interact with an offers API. It abstracts away the complexity of token management, HTTP communication, and response caching while providing a simple, intuitive async API for developers.

### Key Capabilities

- **Fetch Offers**: Retrieve all offers for a specific product with automatic token refresh
- **Register Products**: Register new products with the API
- **Transparent Caching**: HTTP responses are cached automatically, reducing API calls
- **Token Lifecycle Management**: Automatically detects token expiry via JWT decoding and refreshes when needed
- **Configuration**: Flexible setup via environment variables or direct parameter passing
- **CLI Integration**: Built-in command-line tool for quick manual testing

## Quickstart

### Installation

https://test.pypi.org/project/offers-sdk-applifting/

```bash
pip install -i https://test.pypi.org/simple/ offers-sdk-applifting
```

### Setup Configuration

Set the required environment variables:

```bash
export OFFERS_API_BASE_URL="https://api.example.com"
export AUTH_ENDPOINT="auth"
export REFRESH_TOKEN="your_refresh_token_here"
export PERSISTENT_TOKEN_KEY="key_for_secure_refresh_token_storage"
```

Alternatively, create configuration programmatically:

```python
from offers_sdk.config import ApiConfig

config = ApiConfig(
    base_url="https://api.example.com",
    auth_endpoint="auth",
    refresh_token="your_refresh_token_here",
    persistent_auth_token_key="offers_sdk_token"
)
```

### Basic Usage

```python
import asyncio
from uuid import UUID
from offers_sdk.client import OffersClient
from offers_sdk.config import ApiConfig

async def main():
    # Load config from environment
    config = ApiConfig.from_env()

    # Create client
    client = OffersClient(config)

    # Fetch offers for a product
    product_id = UUID("019bc752-0f5c-75ac-8aba-8800f8fa8507")
    offers = await client.get_offers(product_id)

    for offer in offers:
        print(f"Offer {offer.id}: ${offer.price}, {offer.items_in_stock} in stock")

asyncio.run(main())
```

### Using the CLI

This provides an interactive menu to:

- Fetch offers for a product
- Register new products

Credentials and configuration are loaded from environment variables as described above. So, make sure to set them before running the CLI.

#### Registering a Product

```bash
> offers

                        ↑
                       ↑↑↑
                      ↑↑↑↑↑
                     ↑↑↑↑↑↑↑
                    ↑↑↑↑ ↑↑↑↑
                    ↑↑↑   ↑↑↑↑
                   ↑↑↑↑↑↑↑↑↑↑↑
                  ↑↑↑↑↑↑↑↑↑↑↑↑↑
                 ↑↑↑↑       ↑↑↑↑

                      ↑↑↑↑↑
                    ↑↑↑↑↑↑↑↑↑
                    ↑↑↑↑↑↑↑↑↑
                    ↑↑↑↑↑↑↑↑↑
                     ↑ ↑↑↑ ↑
                       ↑↑↑
                        ↑
                        ↑

? Choose an action: Register Product
? Product name: hello-world
? Product description: insanely-great
✅ Product registered with ID: 019bc755-e12e-7250-8075-39caf8ad5b68
```

#### Getting Offers

```bash
? Choose an action: Get Offers
? Product ID:  019bc755-e12e-7250-8075-39caf8ad5b68
                             Offers
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Offer ID                             ┃ Price ┃ Items in Stock ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 112303b4-9760-758b-4018-104ff8e5e288 │ 42652 │ 324            │
├──────────────────────────────────────┼───────┼────────────────┤
│ afd03a1f-a88d-5d5b-24ac-d16ac54b8e1b │ 45617 │ 832            │
├──────────────────────────────────────┼───────┼────────────────┤
│ d6ecc882-20a3-d000-3a28-c6cd6a943922 │ 41138 │ 616            │
├──────────────────────────────────────┼───────┼────────────────┤
│ 7083d342-8966-b6ae-65bf-1ebbc0eb5740 │ 43677 │ 291            │
├──────────────────────────────────────┼───────┼────────────────┤
│ 5a49a0e1-4710-83e3-f27a-d7c6a8f16d6c │ 45520 │ 343            │
├──────────────────────────────────────┼───────┼────────────────┤
│ c37c72e6-1849-510a-ec80-41d64ef418cd │ 40959 │ 147            │
├──────────────────────────────────────┼───────┼────────────────┤
│ 7cfb5195-73a4-d40d-401d-89fbfcc28d50 │ 46089 │ 31             │
├──────────────────────────────────────┼───────┼────────────────┤
│ 6ba7a340-d936-5306-2472-691d220439e6 │ 40915 │ 35             │
└──────────────────────────────────────┴───────┴────────────────┘
```
