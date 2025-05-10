
# Artificial Builders (ABC)
Artificial Builders is an AI-powered GitHub contribution assistant that uses Google Gemini 2.0 to analyze and contribute to open source projects.

## Key Features

- Automated repository analysis using Gemini 2.0
- Intelligent issue creation and management
- Code improvement suggestions
- Documentation analysis and enhancement
- Integration with GitHub's OpenAPI and MCP

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```

3. Set up your environment variables in `.env`:
   - `GITHUB_TOKEN`: Your GitHub personal access token
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `REPO_OWNER`: The repository owner's GitHub username
   - `REPO_NAME`: The repository name

## Usage

The AI agent can be run in two modes:

1. Analysis Mode:
   ```bash
   python ai_agent.py analyze
   ```

2. Contribution Mode:
   ```bash
   python ai_agent.py contribute
   ```

## Architecture

The system consists of:

1. **AI Analysis Module**
   - Uses Google Gemini 2.0 for repository analysis
   - Identifies code improvements, documentation gaps, and testing needs

2. **GitHub Integration Module**
   - Manages GitHub API interactions
   - Handles issue creation and management
   - Implements contribution workflow

3. **Configuration Management**
   - Environment-based configuration
   - Supports multiple repository configurations

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the terms of the MIT license.