# Docker Setup for Iran List Django Application

This document provides instructions for running the Django application using Docker.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)

## Quick Start (Development)

1. **Build and start the containers:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - The Django application will be available at `http://localhost:8000`
   - PostgreSQL will be running on `localhost:5432`

3. **Create a superuser (in a new terminal):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Stop the containers:**
   ```bash
   docker-compose down
   ```

## Production Deployment

1. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your production settings:**
   - Set a strong `SECRET_KEY`
   - Set a secure `POSTGRES_PASSWORD`
   - Configure your domain in `ALLOWED_HOSTS`
   - Update email settings

3. **Update requirements for production:**
   Add to `requirements.txt`:
   ```
   gunicorn==19.9.0
   ```

4. **Build and start production containers:**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

5. **Create superuser:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```

## Docker Files Overview

- **Dockerfile**: Defines the Django application container
- **docker-compose.yml**: Development environment configuration
- **docker-compose.prod.yml**: Production environment with Nginx
- **entrypoint.sh**: Initialization script (migrations, static files)
- **.dockerignore**: Files to exclude from Docker build
- **nginx.conf**: Nginx reverse proxy configuration (production)

## Useful Commands

### Development

```bash
# Start containers
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Execute Django commands
docker-compose exec web python manage.py <command>

# Access Django shell
docker-compose exec web python manage.py shell

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic

# Access PostgreSQL
docker-compose exec db psql -U iran_list_user -d iran_list_db

# Rebuild containers
docker-compose up --build

# Stop and remove containers
docker-compose down

# Stop and remove containers with volumes
docker-compose down -v
```

### Production

```bash
# Start production containers
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Execute commands
docker-compose -f docker-compose.prod.yml exec web python manage.py <command>

# Stop containers
docker-compose -f docker-compose.prod.yml down
```

## Data Persistence

Data is persisted using Docker volumes:
- `postgres_data`: PostgreSQL database
- `static_volume`: Static files (CSS, JS, images)
- `media_volume`: User-uploaded media files

## Environment Variables

The application supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_ENGINE | Database engine | django.db.backends.postgresql |
| DATABASE_NAME | Database name | iran_list_db |
| DATABASE_USER | Database user | iran_list_user |
| DATABASE_PASSWORD | Database password | iran_list_password |
| DATABASE_HOST | Database host | db |
| DATABASE_PORT | Database port | 5432 |
| DEBUG | Debug mode | False |
| ALLOWED_HOSTS | Allowed hosts (comma-separated) | localhost |
| SECRET_KEY | Django secret key | (should be set in production) |
| SITE_ADDRESS | Site URL | http://localhost/ |
| EMAIL_HOST | SMTP host | smtp.mail.yahoo.com |
| EMAIL_PORT | SMTP port | 587 |
| EMAIL_HOST_USER | SMTP username | - |
| EMAIL_HOST_PASSWORD | SMTP password | - |
| EMAIL_USE_TLS | Use TLS for email | True |

## Troubleshooting

### Port already in use
If port 8000 or 5432 is already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port
```

### Database connection errors
Ensure the database container is healthy:
```bash
docker-compose ps
```

### Static files not loading
Run collectstatic:
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### Permission issues
If you encounter permission issues with volumes:
```bash
docker-compose down -v
docker-compose up --build
```

## Notes

- The development setup mounts the local directory, so code changes are reflected immediately
- The production setup uses Nginx as a reverse proxy for better performance
- Always use environment variables for sensitive information
- Never commit `.env` file to version control
