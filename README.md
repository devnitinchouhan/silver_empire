# Silver Jewellery Django API

A Django REST API for managing silver jewellery products and categories with MySQL database support and Docker containerization.

## Features

- Django REST Framework API
- MySQL database
- JWT Authentication
- Category management with hierarchical structure
- Product management
- Docker containerization
- Automatic data initialization
- Nginx for serving static files

## Quick Start with Docker

### Prerequisites

- Docker
- Docker Compose

### Setup

1. Clone the repository and navigate to the project directory

2. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```

3. (Optional) Edit `.env` file to customize configuration:
   - Database credentials
   - Superuser credentials
   - Django settings

4. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

5. The application will be available at:
   - API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - Nginx Proxy: http://localhost

### Default Credentials

- **Superuser Email**: admin@silverjewellery.com
- **Superuser Password**: admin123

(You can change these in the `.env` file)

### Default Categories

The application automatically creates these categories on startup:
- Rings
- Earrings
- Bracelets
- Bangles
- Chains
- Pendants
- Mangalsutra
- Necklaces
- Nose Pin
- Necklace Set

## Docker Services

- **web**: Django application
- **db**: MySQL 8.0 database
- **nginx**: Nginx reverse proxy for static files

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DEBUG | True | Django debug mode |
| SECRET_KEY | django-insecure-... | Django secret key |
| DB_NAME | silver_empire | Database name |
| DB_USER | silveruser | Database user |
| DB_PASSWORD | silverpass123 | Database password |
| DB_HOST | db | Database host |
| DB_PORT | 3306 | Database port |
| SUPERUSER_EMAIL | admin@silverjewellery.com | Admin email |
| SUPERUSER_PASSWORD | admin123 | Admin password |

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login
- `POST /api/auth/register/` - Register
- `POST /api/auth/refresh/` - Refresh token

### Categories
- `GET /api/categories/` - List categories
- `POST /api/categories/` - Create category
- `GET /api/categories/{id}/` - Get category details
- `PUT /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category

### Products
- `GET /api/products/` - List products
- `POST /api/products/` - Create product
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product

## Development

### Running without Docker

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up MySQL database and update `.env` file

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Initialize data:
   ```bash
   python manage.py init_app
   ```

5. Start development server:
   ```bash
   python manage.py runserver
   ```

### Management Commands

- Initialize app data: `python manage.py init_app`
- Create superuser only: `python manage.py init_app --skip-superuser`
- Custom superuser: `python manage.py init_app --superuser-email admin@example.com --superuser-password mypassword`

## Database Schema

The application uses MySQL with the following main models:
- **Customer**: User authentication and profile
- **Category**: Hierarchical product categories
- **Product**: Product information with images

## File Structure

```
├── categories/          # Category app
├── customers/           # Customer/User app
├── products/           # Product app
├── silver_empire/      # Main Django project
├── media/              # User uploaded files
├── staticfiles/        # Static files
├── docker-compose.yaml # Docker composition
├── Dockerfile          # Docker image definition
├── nginx.conf          # Nginx configuration
├── docker-entrypoint.sh # Container startup script
└── requirements.txt    # Python dependencies
```

## Production Considerations

1. Change `SECRET_KEY` in production
2. Set `DEBUG=False` for production
3. Configure proper `ALLOWED_HOSTS`
4. Use environment-specific `.env` files
5. Set up SSL/TLS certificates for HTTPS
6. Configure database backups
7. Use production-grade WSGI server (e.g., Gunicorn)

## Troubleshooting

### Common Issues

1. **MySQL Connection Error**: Ensure MySQL container is running and credentials are correct
2. **Permission Denied**: Make sure `docker-entrypoint.sh` is executable
3. **Port Already in Use**: Change ports in `docker-compose.yaml` if default ports are occupied

### Logs

View container logs:
```bash
docker-compose logs web
docker-compose logs db
docker-compose logs nginx
```

### Reset Database

To completely reset the database:
```bash
docker-compose down -v
docker-compose up --build
```