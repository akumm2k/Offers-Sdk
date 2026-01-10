from container import Container


if __name__ == "__main__":
    container = Container()
    container.config.base_url.from_env("OFFERS_API_BASE_URL")
    container.config.auth_endpoint.from_env("AUTH_ENDPOINT")
    container.config.refresh_token.from_env("REFRESH_TOKEN")
