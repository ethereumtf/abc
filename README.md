# Artificial Builders (ABC)

A decentralized AI framework where autonomous AI agents collaborate on GitHub projects. This system includes multiple specialized AI agents (powered by Gemini 2.0 Flash) that autonomously manage issues, write code contributions, and perform security checks on target GitHub repositories.

## Overview

Artificial Builders demonstrates an end-to-end workflow of AI agents contributing to GitHub repositories with the following capabilities:

- **Understanding Repositories**: Connect to specified GitHub repos to analyze their structure and documentation
- **Managing Issues**: Identify potential problems or improvements and create detailed GitHub issues
- **Contributing Code**: Propose changes by creating branches and submitting pull requests
- **Security Auditing**: Scan repositories for vulnerabilities or privacy concerns
- **Logging Activities**: Record all agent actions to a transparent audit trail
- **Token Rewards**: Simulate a token economy (ABC Token) to incentivize contributions

## Key Features

- Three specialized AI agents:
  - **Issue Manager**: Creates detailed GitHub issues based on repository analysis
  - **Code Contributor**: Submits pull requests to address open issues
  - **Security Auditor**: Identifies vulnerabilities and creates security reports
- Autonomous operation with scheduled runs
- ABC Token reward system for tracking contributions
- Dashboard interface for monitoring agent activities and token economy
- Firestore database for logging and persistent storage

## Technologies

- **Frontend**: React with Tailwind CSS
- **Backend**: Node.js with Express
- **AI**: Google's Gemini 2.0 Flash LLM
- **Database**: Firebase Firestore
- **External APIs**: GitHub REST API, Gemini API

## Getting Started

### Prerequisites

- Node.js 16+
- Firebase account
- GitHub account with a personal access token
- Gemini API key

### Installation

TBD

## License

MIT
