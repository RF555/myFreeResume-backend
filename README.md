# myFreeResume Backend

FastAPI backend for myFreeResume — a free resume and cover letter builder. Provides JWT auth (including OAuth via Google, GitHub, and LinkedIn), user profile management, job type and entry CRUD, and DOCX document generation.

---

## Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd myFreeResume-backend

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file (see Environment Variables below)
cp .env.example .env   # or create manually

# 5. Run the development server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `MONGODB_URI` | Yes | MongoDB connection string |
| `JWT_SECRET` | Yes | Secret key for access tokens and session signing |
| `JWT_REFRESH_SECRET` | Yes | Secret key for refresh tokens |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | Access token lifetime in minutes (default: 15) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | No | Refresh token lifetime in days (default: 7) |
| `FRONTEND_URL` | No | Allowed CORS origin (default: `http://localhost:5173`) |
| `GOOGLE_CLIENT_ID` | No | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth client secret |
| `GITHUB_CLIENT_ID` | No | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | No | GitHub OAuth client secret |
| `LINKEDIN_CLIENT_ID` | No | LinkedIn OAuth client ID |
| `LINKEDIN_CLIENT_SECRET` | No | LinkedIn OAuth client secret |

---

## API Endpoints

### Auth — `/api/auth`
| Method | Path | Description |
|---|---|---|
| POST | `/register` | Register with email + password |
| POST | `/login` | Login with email + password |
| POST | `/logout` | Invalidate refresh token |
| POST | `/refresh` | Rotate refresh token, return new access token |
| GET | `/oauth/{provider}` | Start OAuth flow (`google`, `github`, `linkedin`) |
| GET | `/oauth/{provider}/callback` | OAuth provider callback |

### Users — `/api/users`
| Method | Path | Description |
|---|---|---|
| GET | `/me` | Get current user profile |
| PATCH | `/me` | Update current user profile |

### Job Types — `/api/job-types`
| Method | Path | Description |
|---|---|---|
| GET | `/` | List all job types for current user |
| POST | `/` | Create a job type |
| GET | `/{id}` | Get a job type |
| PUT | `/{id}` | Update a job type |
| DELETE | `/{id}` | Delete a job type |

### Entries — `/api/entries`
| Method | Path | Description |
|---|---|---|
| GET | `/` | List entries (filterable by `job_type_id`) |
| POST | `/` | Create an entry |
| GET | `/{id}` | Get an entry |
| PUT | `/{id}` | Update an entry |
| DELETE | `/{id}` | Delete an entry |
| POST | `/{id}/clone` | Clone an entry |

### Documents — `/api/documents`
| Method | Path | Description |
|---|---|---|
| POST | `/resume` | Generate and download resume DOCX |
| POST | `/cover-letter` | Generate and download cover letter DOCX |

### Health
| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |

---

## Running Tests

```bash
# Run all unit tests
.venv/Scripts/python -m pytest tests/ -v

# Run only service tests
.venv/Scripts/python -m pytest tests/test_services/ -v

# With coverage (if pytest-cov is installed)
.venv/Scripts/python -m pytest tests/ --cov=app --cov-report=term-missing
```
