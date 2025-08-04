# National Park Service MCP Server

An open-source MCP server for managing and processing data related to the National Park Service. This project provides MCP-compliant tools for retriving  park information, visitor management, and more.

## Table of Contents

- [Getting Started](#getting-started)
- [Repository Structure](#repository-structure)
- [Environment Variables](#environment-variables)
- [MCP API Documentation](#mcp-api-documentation)
- [Contributing](#contributing)
- [License](#license)


## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v16+)
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)
- [PostgreSQL](https://www.postgresql.org/) or your preferred database

### Installation

1. Create a virtual environment and activate it:

  ```bash
  uv venv .venv
  source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
  ```

2. Sync dependencies from `pyproject.toml` (if present):

  ```bash
  uv sync
  ```

3. To install additional requirements during development:

  ```bash
  uv pip install -r requirements.txt
  ```

  4. To test the server locally:

    ```bash
    uv run server.py
    ```
    > **Note:** The instructions above are intended for local development and testing. In production, the MCP server is expected to run remotely via Smithery.ai.

## MCP Marketplace

This server is open-sourced and available in the MCP Marketplace: [View on Smithery.ai](https://smithery.ai/server/@harish-anandaramanujam/national-park-service-mcp-server)

## Repository Structure

```
.
├── src/
│   ├── api_utils.py      # To handle API calls to NSP server
│   ├── models.py         # Pydantic Args to get input from LLMs in specific format
├── server.py             # Main python that defines @mcp.tools and its function
│── README.md
├── Dockerfile            # Docker configuration for containerizing the server
├── smithery.yaml         # Smithery  configuration
├── LICENSE               # MIT license information
└── README.md
```

## Environment Variables

Create a `.env` file in the root directory. Required variables include:

```
NPS_API_KEY = "***"
```


## Contributing

We welcome contributions from the community! If you would like to contribute, please follow these steps:

1. Fork this repository.
2. Create a new branch for your changes.
3. Make your improvements or fixes.
4. Open a pull request with a clear description of your changes.

If you have any questions or suggestions, feel free to open an issue. Thank you for helping improve this project!

## License

This project is licensed under the [MIT License](LICENSE).
