# Candidate Hiring Project

A system to manage candidate hiring processes, including resume parsing, profile enrichment.

## Features

- **Authentication**:

  - Secure login with rate limiting.
  - JWT-based authentication for API access.

- **Candidate Management**:

  - Create, update, and retrieve candidate profiles.
  - Search candidates by skills with pagination.

- **Resume Parsing with AI (Grok API)**:

  - Extract skills and information from uploaded resumes (PDF/Word).
  - Background task processing for parsing resumes.

- **Profile Enrichment with AI (Grok API)**:

  - Enrich candidate profiles with external data.
  - Background task processing for enrichment.

- **Task Queue**:

  - Redis-backed task queue for processing candidate-related tasks.
  - Retry mechanism for failed tasks.

- **Email Notifications (Resend API)**:

  - Email sending notifications after queue processing.

- **Caching**:

  - Redis-based caching for frequently accessed data (e.g., candidate profiles).

- **Metrics**:
  - Real-time metrics for task processing (e.g., processed count, failed count, queue length).

## How to Run the App (Using Docker with PostgreSQL)

- Install Docker Desktop
- Run `docker-compose build --no-cache`
- Run `docker-compose up`
- Run `docker compose down  --volumes --remove-orphans` to stop all services

## Environment Variables

### Database

- `DATABASE_URL`: Postgres database.

### JWT Configuration

- `SECRET_KEY`: Secret key for signing JWT tokens.
- `ALGORITHM`: Algorithm used for JWT tokens. Example: `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time for access tokens in minutes.

### Temporary Admin Credentials

- `TEMP_ADMIN_EMAIL`: Email for the temporary admin account.
- `TEMP_ADMIN_PASSWORD`: Password for the temporary admin account.

### Resend API Configuration

- `RESEND_API_KEY`: API key for Resend (used for email notifications).
- `RESEND_EMAIL_ADDRESS`: Email address used for sending notifications.

### Groq API Configuration

- `GROQ_API_KEY`: API key for Groq (used for AI-based resume parsing and enrichment).

### Redis

- `REDIS_HOST`: Hostname for Redis. Example: `redis`.
- `REDIS_PORT`: Port for Redis. Example: `6379`.
- `REDIS_DB`: Redis database index. Example: `0`.

### Queue Configuration

- `REDIS_QUEUE_NAME`: Name of the Redis queue for task processing.
- `REDIS_RETRY_QUEUE_NAME`: Name of the Redis retry queue for failed tasks.
- `REDIS_LOCK_PREFIX`: Prefix for Redis locks.

### Worker Configuration

- `REDIS_LOCK_TTL`: Time-to-live (TTL) for Redis locks in seconds. Example: `30`.
- `WORKER_POLLING_INTERVAL`: Polling interval for the worker in seconds. Example: `5`.
- `WORKER_MAX_RETRIES`: Maximum number of retries for failed tasks. Example: `3`.

## API Endpoints

### Authentication

- `POST /auth/login`: Login and retrieve a JWT token.

### Candidates

- `POST /candidates`: Create a new candidate.
- `GET /candidates/{candidate_id}`: Retrieve a candidate by ID.
- `GET /candidates`: List candidates with optional skill filtering.
- `PUT /candidates/{candidate_id}`: Update a candidate's details.
- `POST /candidates/{candidate_id}/resume-parsing`: Enqueue a resume parsing task for a candidate.
- `POST /candidates/{candidate_id}/profile-enrichment`: Enqueue a profile enrichment task for a candidate.
- `GET /candidates/queue/metrics`: Retrieve queue processing metrics.

### Applications

- `POST /applications`: Submit a new job application.
- `GET /applications/candidate/{candidate_id}`: List all applications for a specific candidate, optionally filtered by status.
- `PATCH /applications/{application_id}`: Update the status of a specific application.
