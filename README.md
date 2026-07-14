# WearItright

> WearItRight is a smart, web-based styling application designed to simplify daily outfit planning. It helps users — from fashion beginners to enthusiasts — create appropriate looks by combining real-time weather, occasion, personal style, and items from their own digital closet. Unlike apps that focus on shopping or inspiration, WearItRight solves the “I have clothes but nothing to wear” problem with fast, personalized recommendations tailored to what users already own. The platform is mobile and desktop friendly, with an intuitive interface that makes styling accessible for everyone.

## Team

| Role | Name |
|---|---|
| Product Owner | Lalit |
| Scrum Master | Sandrin|
| Developer | Brinda(Vaishnavi) |
| Developer |Greshma |


## Project Overview

WearItRight solves daily outfit anxiety for students, professionals, and fashion users of all levels by turning clothes they already own into smart recommendations. Using weather, occasion, and personal style, it delivers complete outfits — cutting decision fatigue and promoting sustainable, practical styling.

## Architecture

_Add your architecture diagram here (C4 Context or Container diagram). Update this as the project evolves._

```
service-a  ──►  service-b
    │
    ▼
  database
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | |
| Backend | |
| Database | |
| Deployment | |

## Getting Started

### Quick Start (Local Development)

For **running locally without Docker**, see [SETUP.md](SETUP.md) for step-by-step instructions.

Quick command:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

The app will be available at `http://localhost:5000`.

### Prerequisites (Docker)

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed
- Git

### Run with Docker

```bash
git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>
cp .env.example .env   # fill in your values
docker compose up --build
```

The app will be available at `http://localhost:3000`.

### Run with Flask

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Repository Structure

```
├── app.py                  # App entry point
├── README.md
├── requirements.txt
├── backend/                # Server-side Flask application
│   ├── app.py              # Backend application factory
│   ├── auth/               # Authentication routes and logic
│   ├── common/             # Shared models and helpers
│   ├── config/             # Database and app settings
│   ├── controllers/        # Request handling layer
│   ├── middleware/         # Security and request middleware
│   ├── models/             # Backend model package exports
│   ├── routes/             # Route package exports
│   ├── services/           # Business logic services
│   └── utils/              # Shared backend utilities
├── frontend/               # Client-facing templates and static assets
│   ├── templates/          # Flask HTML templates
│   ├── static/             # CSS, JS and images
│   ├── components/         # Reusable UI components (future additions)
│   ├── pages/              # Page-level frontend organization
│   └── services/           # Frontend API helpers (future additions)
├── docs/                   # Product and architecture documentation
└── docker-compose.yml
```

## Documentation

- [Vision Document](docs/vision.md)


## License

MIT
