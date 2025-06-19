# Lenseshot Docker Branch

This branch containerizes the Lenseshot Flask application and MySQL database using Docker and Docker Compose. It provides an easy way to run the entire stack locally or in production, ensuring consistent environments and simple setup.

---

## Features

- **Flask app** runs in its own container
- **MySQL database** runs in a separate container with persistent storage
- **Docker Compose** manages multi-container orchestration
- **Hot reloading** (optional, via Docker volumes) for development

---

## Getting Started

### 1. **Clone the Repository**

```sh
git clone https://github.com/yourusername/lenseshot.git
cd lenseshot
git checkout docker
```

### 2. **Configure Environment (Optional)**

- By default, the database connection is set up for Docker Compose.
- If you want to override settings, edit `app/config.py` or use environment variables.

### 3. **Build and Start the Stack**

```sh
docker-compose up --build -d
```

- This builds the Flask app image and starts both the web and database containers.
- The Flask app will be available at [http://localhost:5000](http://localhost:5000).

### 4. **Initialize the Database**

Run the following command to create all tables:

```sh
docker-compose exec web python
from app import create_app, db
app = create_app()
with app.app_context():
      db.create_all()
```

---

## Development Tips

- **Live code reload:** If you use Docker volumes (see `docker-compose.yml`), code changes on your host are reflected instantly in the container.
- **Logs:** View logs with `docker-compose logs -f`.
- **Stop the stack:**  
  ```sh
  docker-compose down
  ```

---

## Troubleshooting

- **Port conflicts:** If port 3306 (MySQL) or 5000 (Flask) is in use, change the host port in `docker-compose.yml`.
- **Database persistence:** Data is stored in a Docker volume (`db_data`) and will persist unless you remove the volume.

---

## Useful Commands

- **Rebuild and restart containers:**
  ```sh
  docker-compose up --build -d
  ```
- **Stop containers:**
  ```sh
  docker-compose down
  ```
- **View running containers:**
  ```sh
  docker-compose ps
  ```
- **Access a shell in the web container:**
  ```sh
  docker-compose exec web sh
  ```

---

## Notes

- The `.docker` directory is ignored by git as it contains only local Docker cache files.
- For production, review security settings and environment variables.

---
