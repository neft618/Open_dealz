# OpenDealz - Freelance Platform MVP

A web application connecting IT project customers and executors via programmatic smart contracts, featuring escrow, dispute resolution, and cryptographic audit trails.

## Features

- **User Roles**: Customer, Executor, Admin
- **Order Management**: Create, browse, and apply to orders
- **Contract Builder**: Step-by-step contract creation with drag-and-drop clause ordering
- **Escrow System**: Secure funds locking and release
- **Dispute Resolution**: Admin-mediated arbitration
- **Audit Trail**: SHA-256 hashed immutable logs
- **File Storage**: Supabase Storage for portfolios and deliverables

## Tech Stack

### Backend
- Python 3.11, FastAPI, Uvicorn (ASGI)
- SQLAlchemy 2.x async, PostgreSQL (Supabase)
- JWT authentication, bcrypt hashing
- Supabase Storage integration
- Aiosmtplib for email notifications

### Frontend
- React 18, JavaScript ES2020
- React Router 6, Axios for API calls
- Zustand for state management
- Tailwind CSS for styling
- React Hook Form + Zod validation
- @dnd-kit for drag-and-drop
- Recharts for data visualization
- React Hot Toast for notifications

### Infrastructure
- Docker Compose for local development
- Nginx reverse proxy
- Alembic for database migrations

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Supabase account and project
- Node.js 18+ and npm (for local frontend dev)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/opendealz.git
cd opendealz
```

### 2. Supabase Setup
1. Create a new Supabase project
2. Go to SQL Editor and run the migration SQL (see database schema below)
3. Create two storage buckets:
   - `portfolios` (public)
   - `deliverables` (private)
4. Get your project URL, anon key, and service role key from Settings > API
5. For migrations, use the Session mode connection string (port 5432)

### 3. Environment Variables
Copy `.env.example` to `.env` and fill in your values:

```bash
# Backend
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
SECRET_KEY=your-256-bit-secret-key
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
# ... other vars

# Frontend (if running separately)
VITE_API_URL=http://localhost:8000/api/v1
```

### 4. Run with Docker Compose
```bash
docker-compose up --build
```

This starts:
- Backend on http://localhost:8000
- Frontend on http://localhost:3000
- Nginx proxy on http://localhost:80

### 5. Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API docs.

## Environment Variables Table

| Variable | Description | Example |
|----------|-------------|---------|
| APP_ENV | Environment | development |
| DATABASE_URL | Supabase DB URL | postgresql+asyncpg://... |
| SECRET_KEY | JWT secret | your-256-bit-key |
| SUPABASE_URL | Supabase project URL | https://xxx.supabase.co |
| SUPABASE_SERVICE_ROLE_KEY | Service role key | eyJ... |
| SMTP_HOST | Email SMTP host | smtp.gmail.com |
| SMTP_PORT | SMTP port | 587 |
| SMTP_USERNAME | SMTP username | your-email@gmail.com |
| SMTP_PASSWORD | SMTP password | your-app-password |
| PLATFORM_FEE_PERCENT | Platform fee % | 3.0 |
| VITE_API_URL | Frontend API URL | http://localhost:8000/api/v1 |

## Project Structure

```
opendealz/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, security, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── routers/       # API endpoints
│   │   └── dependencies.py # Auth dependencies
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic/           # Migrations
├── frontend/
│   ├── src/
│   │   ├── api/           # API client functions
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── store/         # Zustand stores
│   │   ├── hooks/         # Custom hooks
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests
5. Submit a pull request

## License

MIT License