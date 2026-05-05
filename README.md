[![Frontend CI](https://github.com/swe-students-spring2026/5-final-stonefly_ring/actions/workflows/frontend.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-stonefly_ring/actions/workflows/frontend.yml)
[![API CI](https://github.com/swe-students-spring2026/5-final-stonefly_ring/actions/workflows/api.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-stonefly_ring/actions/workflows/api.yml)
[![Database CI](https://github.com/swe-students-spring2026/5-final-stonefly_ring/actions/workflows/database.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-stonefly_ring/actions/workflows/database.yml)

# Software Engineering Final Project

# CostShare App

CostShare helps roommates track shared purchases (for example groceries, paper towels, and other household items), calculate who owes whom, and avoid uneven expense sharing over time.

## Team
- [Adam Shin](https://github.com/aus2003)
- [Han Xiao](https://github.com/vick12333)
- [@username3](https://github.com/username3)
- [@username4](https://github.com/username4)
- [@username5](https://github.com/username5)

## Docker Container Images
- Frontend image: `docker.io/<DOCKER_HUB_USERNAME>/swe-project-5-frontend`
- API image: `docker.io/<DOCKER_HUB_USERNAME>/swe-project-5-api`
- Database init image: `docker.io/<DOCKER_HUB_USERNAME>/swe-project-5-db`

Replace `<DOCKER_HUB_USERNAME>` with your Docker Hub username.

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Example `.env`:

```env
MONGO_URI=mongodb://mongodb:27017/
MONGO_DBNAME=splitring
FLASK_SECRET_KEY=change-me-to-a-random-long-string
API_SHARED_SECRET=change-me-to-a-random-long-string
API_URL=http://api:5001
```

### Database Setup

- `database/init_db.py` creates required collections and indexes.
- `database/seed_data.py` inserts starter users and starter friendships.
- In Docker Compose mode, init runs automatically through the `db-init` service.
- Seed data can be run manually after startup:

```bash
source .venv/bin/activate
python database/seed_data.py
```

## Running the Project

### Prerequisites

- Docker Desktop (recommended path), or
- Python 3.11+ and a local MongoDB instance for manual startup

### With Docker Compose

```bash
# from repo root
cp .env.example .env
docker compose up --build
```

Services:
- Frontend: `http://localhost:3000`
- API: `http://localhost:5001`
- MongoDB: `mongodb://localhost:27017`

### Without Docker Compose

1) Start MongoDB locally.

2) Initialize and seed database:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r database/requirements.txt
export MONGO_URI="mongodb://localhost:27017/"
export MONGO_DBNAME="splitring"
python database/init_db.py
python database/seed_data.py
```

3) Start API:

```bash
source .venv/bin/activate
python -m pip install -r api/requirements.txt
export MONGO_URI="mongodb://localhost:27017/"
export MONGO_DBNAME="splitring"
export API_SHARED_SECRET="change-me"
python api/app.py
```

4) Start frontend:

```bash
source .venv/bin/activate
python -m pip install -r frontend/requirements.txt
export API_URL="http://localhost:5001"
export FLASK_SECRET_KEY="change-me"
python frontend/app.py
```

## Testing and Coverage

These commands verify unit tests and coverage for API, database, and frontend subsystems.

```bash
# from repo root
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r api/requirements.txt -r database/requirements.txt -r frontend/requirements.txt
python -m pip install pytest pytest-cov

# run all tests
python -m pytest

# run coverage summary
python -m pytest --cov=api --cov=database --cov=frontend --cov-report=term-missing
```
