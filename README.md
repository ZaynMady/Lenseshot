
## 🏗 Architecture Overview

The backend is split into specialized services to ensure separation of concerns and independent scalability:

* **Projects Service**: Manages high-level project metadata, ownership, and organization.
* **Scripts Service**: A dedicated engine for creating and managing industry-standard screenplays with support for custom templates.
* **Shared Utility Library (`my-util-lib`)**: A custom-built internal package used by all microservices to provide consistent database ORM patterns, Cloudflare R2 storage abstractions, and Supabase JWT authentication logic.

## 🛠 Tech Stack

* **Framework**: Flask (RESTful API)
* **Database**: Supabase (PostgreSQL) managed via SQLAlchemy ORM.
* **Storage**: Cloudflare R2 (S3-compatible) for hosting screenplay files and project assets.
* **Auth**: Supabase Auth with custom JWT validation middleware.
* **Containerization**: Docker & Docker Compose for local development and production parity.
* **CI/CD**: Automated deployment via Render using a `render.yaml` blueprint.

## 🚀 Key Features implemented

### Microservice Orchestration

* **Service Communication**: The Projects Service communicates with the Scripts Service to perform cascading deletes—ensuring that when a project is removed, all associated screenplays are also purged from storage and the database.
* **Dockerized Environments**: Each service is isolated in its own container, using multi-stage-like logic to install the local `my-util-lib` before service-specific requirements.

### Advanced Storage Logic

* **Cloudflare R2 Integration**: Implemented a robust storage abstraction that handles file CRUD operations, including a `delete_many` feature for cleaning up project directories efficiently.

### Security & Reliability

* **Stateless Authentication**: Custom decorators verify Supabase-issued JWTs across all protected routes.
* **Comprehensive Testing**: Over 90% logic coverage with `pytest`, utilizing `unittest.mock` to simulate storage and database failures to ensure graceful error handling and database rollbacks.

## 🔧 Installation & Setup

1. **Clone the repository**:
```bash
git clone [repository-url]

```


2. **Environment Configuration**:
Create `.env` files in both `/projects` and `/scripts` directories based on the required keys (DATABASE_URL, SUPABASE_JWT_SECRET, CLOUDFLARE credentials, etc.).
3. **Run with Docker Compose**:
```bash
docker-compose up --build

```


* Projects API will be available at `http://localhost:7000`.
* Scripts API will be available at `http://localhost:8000`.



## 🧪 Running Tests

The project uses `pytest` for unit testing.

```bash
pytest

```

## 📈 Roadmap

* **PDF Export Engine**: Integration of a dedicated service to render screenplays into industry-standard PDFs.
* **Real-time Collaboration**: Transitioning screenplay editing to WebSockets for live multi-user interaction.
* **Pagination Logic**: Implementing server-side pagination for long-form feature scripts.
