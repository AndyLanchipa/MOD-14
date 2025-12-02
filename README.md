# Calculation API

A robust FastAPI application for mathematical calculations with user management, built with SQLAlchemy and comprehensive testing.

**Docker Hub**: [andylanchipa/calculation-app](https://hub.docker.com/r/andylanchipa/calculation-app)

## Module 13 Features

This module implements complete JWT-based authentication with front-end interface and end-to-end testing:

### JWT Authentication System
- **User Registration**: POST `/api/users/register` with Pydantic validation
- **User Login**: POST `/api/users/login` with OAuth2 password flow
- **JWT Token Generation**: HS256 algorithm with 30-minute expiration
- **Password Security**: Bcrypt hashing with proper salt rounds
- **Protected Endpoints**: All calculation routes require valid JWT tokens
- **Current User Retrieval**: GET `/api/users/me` with token validation

### Front-End Interface
- **Registration Page**: `/static/register.html`
  - Username validation (3-50 chars, alphanumeric + underscore)
  - Email validation with proper format checking
  - Password requirements (8+ chars, uppercase, lowercase, digit)
  - Confirm password matching
  - Real-time client-side validation with visual feedback
  - Error message display for server-side validation failures
  
- **Login Page**: `/static/login.html`
  - Username/email and password fields
  - Client-side validation
  - JWT token storage in localStorage
  - Success/error message handling
  - Automatic redirect to dashboard on success
  
- **Dashboard Page**: `/static/dashboard.html`
  - Protected route with authentication check
  - Display current user information
  - Logout functionality
  - Token expiration handling
  - Automatic redirect to login if unauthenticated

### Playwright End-to-End Tests
- **Positive Test Cases**:
  - Successful registration with valid data
  - Form validation feedback with success styling
  - Successful login with correct credentials
  - JWT token storage verification
  - Dashboard user information display
  - Complete authentication flow from registration to dashboard
  - Logout functionality
  - Authentication redirect flows
  
- **Negative Test Cases**:
  - Short password validation (< 8 characters)
  - Password missing uppercase letter
  - Password missing lowercase letter
  - Password missing digit
  - Mismatched password confirmation
  - Invalid email format
  - Short username (< 3 characters)
  - Invalid username characters
  - Duplicate username registration
  - Wrong password on login
  - Nonexistent username login
  - Empty form field validation
  - Unauthenticated access protection

### CI/CD Pipeline Integration
- **GitHub Actions Workflow**:
  - PostgreSQL service container for integration tests
  - Automated linting (flake8, black, isort)
  - Unit and integration test execution
  - Playwright browser installation (Chromium)
  - E2E test execution in headless mode
  - Test result artifact uploads
  - Docker image build and push to Docker Hub
  - Security scanning (Bandit, Safety)

## Features

- **Mathematical Operations**: Support for addition, subtraction, multiplication, and division
- **User Management**: User registration and calculation history tracking
- **Factory Pattern**: Extensible calculation operations using the factory design pattern
- **Data Validation**: Comprehensive input validation with Pydantic schemas
- **Database Integration**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Comprehensive Testing**: Unit and integration tests with 80%+ code coverage
- **CI/CD Pipeline**: Automated testing and Docker deployment via GitHub Actions

## Technology Stack

- **Backend**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy 2.0.23
- **Validation**: Pydantic 2.4.2
- **Migrations**: Alembic 1.13.1
- **Testing**: Pytest with coverage reporting
- **Containerization**: Docker with multi-stage builds
- **CI/CD**: GitHub Actions with PostgreSQL service container

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd calculation-api
   ```

2. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the application**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

### Front-End Access

Once the application is running, you can access the web interface:

- **Registration Page**: `http://localhost:8000/static/register.html`
- **Login Page**: `http://localhost:8000/static/login.html`
- **Dashboard**: `http://localhost:8000/static/dashboard.html` (requires authentication)
- **API Documentation**: `http://localhost:8000/docs`

### Front-End Features

The application includes a complete authentication interface:

- **User Registration**: 
  - Client-side validation for username, email, and password
  - Real-time feedback for input errors
  - Password requirements: 8+ characters, uppercase, lowercase, and digit
  - Username validation: 3-50 characters, alphanumeric and underscore only
  
- **User Login**:
  - Secure JWT token-based authentication
  - Token storage in browser localStorage
  - Automatic redirect to dashboard on success
  
- **Dashboard**:
  - Display user information
  - Logout functionality
  - Protected route that requires authentication
  - Token expiration handling with automatic redirect

### Docker Deployment

1. **Build and run with Docker**
   ```bash
   docker build -t calculation-app .
   docker run -p 8000:8000 -e DATABASE_URL="your-db-url" calculation-app
   ```

2. **Using Docker Compose** (recommended for development)
   ```bash
   docker-compose up -d
   ```

## API Documentation

Once the application is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

### API Endpoints

#### User Endpoints

**Register a New User**
```http
POST /api/users/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123"
}

Response: 201 Created
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2025-11-30T22:30:00Z"
}
```

**Login and Get Access Token**
```http
POST /api/users/login
Content-Type: application/x-www-form-urlencoded

username=testuser&password=SecurePass123

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Get Current User Information** (Protected)
```http
GET /api/users/me
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2025-11-30T22:30:00Z"
}
```

#### Calculation Endpoints (All Protected)

**Create a Calculation**
```http
POST /api/calculations
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "a": 10.5,
  "b": 5.5,
  "type": "ADD"
}

Response: 201 Created
{
  "id": 1,
  "a": 10.5,
  "b": 5.5,
  "type": "ADD",
  "result": 16.0,
  "user_id": 1,
  "created_at": "2025-11-30T22:30:00Z",
  "updated_at": "2025-11-30T22:30:00Z"
}
```

**Browse User's Calculations** (with pagination)
```http
GET /api/calculations?skip=0&limit=20
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": 3,
    "a": 6.0,
    "b": 7.0,
    "type": "MULTIPLY",
    "result": 42.0,
    "user_id": 1,
    "created_at": "2025-11-30T22:32:00Z",
    "updated_at": "2025-11-30T22:32:00Z"
  },
  {
    "id": 2,
    "a": 20.0,
    "b": 8.0,
    "type": "SUB",
    "result": 12.0,
    "user_id": 1,
    "created_at": "2025-11-30T22:31:00Z",
    "updated_at": "2025-11-30T22:31:00Z"
  }
]
```

**Read Specific Calculation**
```http
GET /api/calculations/{id}
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "a": 10.5,
  "b": 5.5,
  "type": "ADD",
  "result": 16.0,
  "user_id": 1,
  "created_at": "2025-11-30T22:30:00Z",
  "updated_at": "2025-11-30T22:30:00Z"
}
```

**Edit a Calculation** (partial update)
```http
PATCH /api/calculations/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "a": 20.0,
  "type": "MULTIPLY"
}

Response: 200 OK
{
  "id": 1,
  "a": 20.0,
  "b": 5.5,
  "type": "MULTIPLY",
  "result": 110.0,
  "user_id": 1,
  "created_at": "2025-11-30T22:30:00Z",
  "updated_at": "2025-11-30T22:35:00Z"
}
```

**Delete a Calculation**
```http
DELETE /api/calculations/{id}
Authorization: Bearer <access_token>

Response: 204 No Content
```

**Available Calculation Types**: `ADD`, `SUB`, `MULTIPLY`, `DIVIDE`

## Testing

The project includes comprehensive test coverage across all layers:

### Test Suite Overview
- **Unit Tests**: Factory pattern, schemas, authentication, and user services (31 tests)
- **Integration Tests**: Database operations and API endpoints (50+ tests)
- **Route Tests**: User registration/login and calculation CRUD (40+ tests)
- **E2E Tests**: Playwright end-to-end authentication flow tests (20+ tests)
- **Coverage**: 80%+ code coverage with detailed reporting

### Run All Tests
```bash
# Run all tests with coverage (excluding E2E)
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing -m "not e2e"

# Expected output: 80+ tests passing
```

### Run Playwright E2E Tests

**Prerequisites**: Install Playwright browsers first:
```bash
# Install Playwright and browsers
pip install playwright pytest-playwright
playwright install chromium

# Ensure the FastAPI server is running
uvicorn main:app --reload  # In a separate terminal
```

**Run E2E Tests**:
```bash
# Run all E2E tests
pytest tests/e2e/ -v -m e2e

# Run with headed browser to see the tests
pytest tests/e2e/ -v -m e2e --headed

# Run specific E2E test class
pytest tests/e2e/test_auth_e2e.py::TestRegistrationPositive -v
pytest tests/e2e/test_auth_e2e.py::TestLoginPositive -v
pytest tests/e2e/test_auth_e2e.py::TestRegistrationNegative -v
pytest tests/e2e/test_auth_e2e.py::TestLoginNegative -v

# Generate HTML report
pytest tests/e2e/ -v -m e2e --html=e2e-report.html --self-contained-html
```

**E2E Test Coverage**:

**Positive Scenarios**:
- Successful registration with valid credentials
- Form validation feedback with success styling
- Successful login after registration
- JWT token storage in localStorage
- Dashboard displays user information
- Logout functionality clears token
- Authentication redirect flows

**Negative Scenarios**:
- Registration with short password (< 8 characters)
- Password missing uppercase letter
- Password missing lowercase letter
- Password missing digit
- Mismatched password confirmation
- Invalid email format
- Short username (< 3 characters)
- Invalid username characters
- Duplicate username registration
- Login with wrong password
- Login with nonexistent username
- Login with empty fields
- Unauthenticated dashboard access redirects to login

### Run Specific Test Categories
```bash
# User route tests (registration, login, authentication)
pytest tests/test_user_routes.py -v

# Calculation route tests (BREAD operations)
pytest tests/test_calculation_routes.py -v

# Factory pattern tests (12 tests)
pytest tests/test_calculation_factory.py -v

# Schema validation tests (9 tests)
pytest tests/test_calculation_schemas.py -v

# Authentication service tests
pytest tests/test_auth_service.py -v

# Integration tests with database (10 tests)
pytest tests/test_calculation_integration.py -v

# Quick test run without coverage
pytest tests/ -v -m "not e2e"
```

### Test Database Setup
Tests use SQLite by default for isolation. For PostgreSQL integration testing:

```bash
# Set up test database
export TEST_DATABASE_URL="postgresql://testuser:testpass@localhost/testdb"
pytest tests/test_calculation_integration.py -v
```

### Continuous Integration
All tests run automatically on every push via GitHub Actions:
- Linting with flake8, black, and isort
- All unit and integration tests (80+ tests)
- Playwright E2E tests in headless mode
- User and calculation route tests
- Code coverage reporting (minimum 80%)
- Docker image build and push to Docker Hub

### E2E Test Architecture

The E2E testing infrastructure uses Playwright with the following setup:

**Test Server Management**:
- Automatic FastAPI server startup in separate process
- Clean database state for each test using fixtures
- Proper teardown and cleanup after tests

**Browser Context**:
- Tests run in Chromium (configurable in pytest.ini)
- 1280x720 viewport for consistency
- Can run headed or headless mode

**Test Isolation**:
- Each test gets unique user credentials to avoid conflicts
- Database is truncated before and after each test
- Fresh browser page for each test case

## Screenshots

### GitHub Actions Workflow
![GitHub Actions Success](docs/screenshots/github-actions-success.png)
*Successful CI/CD pipeline run with all tests passing including Playwright E2E tests*

### Playwright E2E Tests
![Playwright Tests](docs/screenshots/playwright-tests.png)
*End-to-end authentication flow tests passing*

### Front-End Login Page
![Login Page](docs/screenshots/login-page.png)
*User login interface with client-side validation*

### Front-End Registration Page
![Registration Page](docs/screenshots/registration-page.png)
*User registration form with comprehensive validation*

### Front-End Dashboard
![Dashboard](docs/screenshots/dashboard-page.png)
*Authenticated user dashboard displaying user information*

### API Documentation
![OpenAPI Docs](docs/screenshots/openapi-docs.png)
*Interactive API documentation at /docs*

### Docker Hub
![Docker Hub](docs/screenshots/docker-hub.png)
*Docker images deployed to Docker Hub*

*Note: Screenshots are located in `docs/screenshots/` directory.*

## Architecture

### Models
- **User**: User management with authentication support
- **Calculation**: Mathematical operations with audit trails

### Schemas
- **CalculationCreate**: Input validation for new calculations
- **CalculationRead**: Serialization for API responses  
- **CalculationUpdate**: Partial update validation

### Services
- **CalculationFactory**: Factory pattern for operation extensibility
- Individual operation classes: `AddOperation`, `SubOperation`, `MultiplyOperation`, `DivideOperation`

### Database Design
```sql
-- Users table
users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Calculations table
calculations (
    id SERIAL PRIMARY KEY,
    a FLOAT NOT NULL,
    b FLOAT NOT NULL,
    type VARCHAR(20) NOT NULL,
    result FLOAT,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## CI/CD Pipeline

The project includes a comprehensive GitHub Actions workflow:

### Automated Testing
- **Linting**: Code quality checks with flake8, black, and isort
- **Unit Tests**: Factory pattern and schema validation tests
- **Integration Tests**: Database operations and model relationships
- **Coverage**: Minimum 80% code coverage requirement
- **Security**: Bandit security scanning and dependency safety checks

### Docker Deployment
- **Automated Builds**: Docker images built on every push to main
- **Docker Hub**: Images pushed to Docker Hub registry
- **Multi-arch Support**: Built for multiple platforms
- **Security**: Non-root user and minimal attack surface

### Pipeline Stages
1. **Code Quality**: Linting and formatting checks
2. **Testing**: Unit and integration tests with PostgreSQL
3. **Security**: Vulnerability scanning
4. **Build**: Docker image creation and testing
5. **Deploy**: Push to Docker Hub (main branch only)

## Docker Hub Repository

**Docker Hub**: `https://hub.docker.com/r/<your-username>/calculation-app`

The application is automatically deployed to Docker Hub on every push to the main branch.

### Pull and Run
```bash
# Pull the latest image
docker pull <your-username>/calculation-app:latest

# Run the container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host/db" \
  -e SECRET_KEY="your-secret-key" \
  <your-username>/calculation-app:latest

# Access the application
# API: http://localhost:8000/docs
# Front-end: http://localhost:8000/static/login.html
```

### Available Tags
- `latest`: Most recent build from main branch
- `<commit-sha>`: Specific commit version for reproducibility

**Note**: Replace `<your-username>` with your actual Docker Hub username. Configure `DOCKER_USERNAME` and `DOCKER_TOKEN` secrets in your GitHub repository settings for automated deployment.

## Development Guidelines

### Adding New Operations
1. Create operation class implementing `CalculationOperation` protocol
2. Register in `CalculationFactory._operations`
3. Add to `CalculationType` enum
4. Write comprehensive tests
5. Update documentation

### Database Changes
1. Modify models in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review and edit migration file
4. Apply: `alembic upgrade head`
5. Update tests accordingly

### Testing Standards
- Maintain 80%+ code coverage
- Write both unit and integration tests
- Test error conditions and edge cases
- Use meaningful test descriptions
- Mock external dependencies appropriately

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Production database connection string | `sqlite:///./calculation_app.db` |
| `TEST_DATABASE_URL` | Test database connection string | `sqlite:///./test_calculation_app.db` |
| `SECRET_KEY` | JWT secret key for authentication | Required for production |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `30` |

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `pytest tests/ -v`
5. Commit with conventional commits: `git commit -m "feat: add new operation"`
6. Push and create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review test examples for usage patterns
