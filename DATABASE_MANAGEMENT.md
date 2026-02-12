# Database Management Guide

## Common Issues and Solutions

### Schema Mismatch Errors

If you see errors like:
```
sqlalchemy.exc.OperationalError: no such column: table_name.column_name
```

This means your database schema is out of sync with your models.

## Solution 1: Quick Reset (Development Only)

Use the provided reset script:

```bash
python reset_database.py
```

This will:
- Delete the old database
- Create fresh tables with current schema
- Seed initial data (admin, gallery, videos)

**⚠️ WARNING**: This deletes ALL data!

## Solution 2: Manual Reset

1. Stop the Flask application (Ctrl+C)
2. Delete the database file:
   ```bash
   # Windows PowerShell
   Remove-Item "instance\rst_slamet_riyadi.db" -Force
   
   # Linux/Mac
   rm instance/rst_slamet_riyadi.db
   ```
3. Restart the application:
   ```bash
   python main.py
   ```

## Solution 3: Production (Use Migrations)

For production environments, use Flask-Migrate:

```bash
# Install Flask-Migrate
pip install Flask-Migrate

# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## Default Admin Credentials

After reset, use these credentials to log in as admin:

- **Username**: `slametriyadi`
- **Password**: `surka13rs`

## When to Reset the Database

Reset the database when you:
- Add new columns to existing models
- Remove columns from models
- Change column types or constraints
- Add new models/tables
- Modify relationships between tables

## Development vs Production

- **Development**: It's safe to reset the database using the script
- **Production**: Always use migrations (Flask-Migrate) to preserve data
