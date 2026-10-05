# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.

## Testing

From the repository root, install dependencies and run the backend tests using
the project's virtual environment (activation is not required):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -v
```

If the virtual environment does not exist, create it first with `py -m venv .venv`.
With an activated environment, you can also run `python -m pytest` from the
repository root; the pytest configuration discovers the `tests` directory.

The suite uses FastAPI's `TestClient`, so no running server is needed. Tests
follow the Arrange-Act-Assert pattern and use fresh sample activity data for
each test. Fixtures restore the original data afterward, and tests do not
change the live server's registrations.

Coverage includes activity listing, the frontend redirect, signup and duplicate
rejection, unregistering, missing-email and unknown-activity errors, and signing
up again after unregistering.
