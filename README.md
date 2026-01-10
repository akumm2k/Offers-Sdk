# Offers SDK

## TODO

- [ ] Add unit tests:
  - [ ] Requests client tests
    - [x] Basic GET / POST params and calls
    - [ ] Error handling
  - [ ] Http client refresh token tests
  - [ ] Offers SDK tests
- [ ] Add integration tests:
    - [ ] SDK:with mocked HTTP client injection
- [ ] Add TUI using textual
  - [ ] Map SDK spec page design to TUI components
- [ ] Package and publish to TestPyPI
- [ ] Add Usage docs here


---


### Must Haves

- [ ] Your SDK should feel intuitive and Pythonic
- [ ] Automatically handle token refresh without user intervention
- [ ] Your refresh token is tied to your email and never expires — you only need one
- [ ] Turn your refresh token into access tokens via the auth endpoint
- [ ] Be careful — access tokens expire
- [ ] SDK must be async-first using `async/await` for API calls
- [ ] Use an HTTP client of your choice for API calls
- [ ] Full type hints throughout the codebase
- [ ] Implement comprehensive error handling with meaningful exceptions
- [ ] Write comprehensive test suite for your SDK using `pytest`
- [ ] Add clear README with quickstart guide and examples
- [ ] Push your solution into a git repository (GitHub, GitLab, ...) and send us a link

### You Can Earn Extra Points For

- [ ] Support for multiple HTTP clients (`httpx`, `requests`, `aiohttp`) with configurable backends
- [ ] Consider adding retry logic for transient network failures with exponential backoff
- [ ] Generate SDK methods automatically from OpenAPI specification provided above
- [ ] Provide advanced configuration options (environment variables, config files, etc.)
- [ ] Add advanced SDK features:
  - [ ] CLI companion tool for testing the SDK from command line
  - [ ] Plugin architecture for extensible request/response processing
  - [ ] Add synchronous wrapper on top of async implementation
  - [ ] Caching layer for offer data with configurable TTL
  - [ ] Request middleware hooks for logging, metrics, or custom headers
  - [ ] Batch operations for efficient handling of multiple product registrations
- [ ] Package your SDK for distribution with proper packaging configuration
- [ ] Demonstrate it can be built and installed locally using your preferred tool (`pip`, `uv`, `poetry`, etc.)
- [ ] Optionally test publishing to TestPyPI (the test instance of PyPI)
