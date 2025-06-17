# Resilience Backend Documentation

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **AI Services**: Custom AI agents for chat, mood detection, reframing
- **Authentication**: Supabase Auth integration

## Project Structure

### Main Application (`app/`)

#### **API Layer (`api/v1/`)**
- `auth.py`: Authentication endpoints and user management
- `chat.py`: Chat/conversation endpoints with AI assistant
- `reflections.py`: Reflection creation and management endpoints
- `reframes.py`: Reframe generation and management endpoints
- `wins.py`: Win tracking and management endpoints
- `streaks.py`: Streak tracking and analytics endpoints

#### **Data Models (`models/`)**
- `chat.py`: Chat and conversation data models
- `reflection.py`: Reflection data models and schemas
- `reframe.py`: Reframe data models and schemas
- `win.py`: Win tracking data models and schemas

#### **Core Services (`core/`)**
- `config.py`: Application configuration and environment variables
- `database.py`: Database connection and session management
- `security.py`: Security utilities and authentication helpers

#### **AI Services (`services/ai/`)**
- `base_agent.py`: Base class for AI agents
- `chat_assistant.py`: AI-powered chat assistant
- `mood_detector.py`: Mood analysis and detection service
- `reframe_agent.py`: AI agent for generating reframes/perspective shifts
- `win_generator.py`: AI agent for identifying and generating wins

### Application Entry
- **`main.py`**: FastAPI application setup and configuration

### Testing & Development
- **`tests/`**: Test files for API endpoints and services
- **`test_ai_services.py`**: Tests for AI service functionality
- **`test_api.py`**: API endpoint tests
- **`test_server.py`**: Server integration tests
- **`run_tests.sh`**: Test execution script

## Development Setup

### Dependencies
- **Core**: FastAPI, Uvicorn, Pydantic
- **Database**: Supabase client libraries
- **AI/ML**: Custom AI integration (specific libraries TBD)
- **Testing**: Pytest framework

### Environment Variables
Required for backend operation:
- Database connection strings
- Supabase service keys
- AI service API keys (if applicable)

### Running the Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main:app --reload

# Run tests
./run_tests.sh
# or
python -m pytest
```

## API Architecture
- **RESTful API**: Version 1 endpoints under `/api/v1/`
- **Authentication**: Supabase Auth integration
- **Data Validation**: Pydantic models for request/response validation
- **Database**: Supabase PostgreSQL with ORM integration

## AI Services Architecture
All AI services inherit from `base_agent.py` and provide:
- Standardized input/output interfaces
- Error handling and logging
- Configurable AI model backends
- Conversation context management

### Service Responsibilities
- **Chat Assistant**: Conversational AI for user interactions
- **Mood Detector**: Analyzes user input to detect emotional state
- **Reframe Agent**: Generates alternative perspectives on situations
- **Win Generator**: Identifies positive outcomes and achievements

## Integration Notes
- Frontend communicates via REST API endpoints
- Supabase handles authentication and data persistence
- AI services process user input to provide intelligent responses
- All endpoints return consistent JSON responses with proper error handling