# Jeruyiq API

A comprehensive travel and booking API system built with Python Flask, featuring AI-powered recommendations, multi-database architecture, and extensive travel-related functionalities.

## Features

- User management and authentication
- Property booking system
- Tour management
- Attraction information
- Guide services
- Visa information
- AI-powered recommendations
- Multi-language support
- Real-time chat system

## Tech Stack

- **Framework:** Flask
- **Databases:**
  - PostgreSQL (for structured data)
  - Firebase (for real-time features)
- **AI/ML:** Google Cloud AI Platform (Gemini)
- **Authentication:** JWT
- **Documentation:** OpenAPI/Swagger

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Run the application:
   ```bash
   python app.py
   ```

## Development

- **Code Style:** Follow PEP 8
- **Type Hints:** Required for all new code
- **Testing:** pytest for unit tests

## API Documentation

API documentation is available at `/docs` when running the application.

## License

Copyright © 2025 Jeruyiq
