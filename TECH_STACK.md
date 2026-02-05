# Technical Stack Documentation
## RST Slamet Riyadi Company Profile Website

---

## Table of Contents
1. [Backend Framework](#backend-framework)
2. [Database](#database)
3. [Authentication](#authentication)
4. [File Management](#file-management)
5. [Frontend](#frontend)
6. [AI Integration](#ai-integration)
7. [Deployment](#deployment)

---

## Backend Framework

### **Flask** (Python Web Framework)
- **Version**: Latest
- **Purpose**: Core web application framework
- **Description**: Flask is a lightweight WSGI web application framework in Python. It's designed to make getting started quick and easy, with the ability to scale up to complex applications.
- **Why Flask?**
  - Simple and flexible
  - Easy to learn and use
  - Extensive ecosystem of extensions
  - Perfect for small to medium-sized applications
- **Key Features Used**:
  - Routing (`@app.route()`)
  - Request handling (GET, POST)
  - Template rendering with Jinja2
  - Flash messages for user feedback
  - File upload handling
  - Session management

**Documentation**: https://flask.palletsprojects.com/

---

## Database

### **Flask-SQLAlchemy** (ORM - Object Relational Mapper)
- **Version**: Latest
- **Purpose**: Database abstraction and management
- **Description**: SQLAlchemy is the Python SQL toolkit and ORM that gives application developers the full power and flexibility of SQL. Flask-SQLAlchemy is an extension for Flask that adds support for SQLAlchemy.
- **Database Type**: SQLite (file-based database)
- **Database File**: `rst_slamet_riyadi.db`
- **Why SQLAlchemy?**
  - Pythonic way to work with databases
  - Prevents SQL injection attacks
  - Easy to define models and relationships
  - Automatic schema migration support
  - Cross-database compatibility

**Database Models**:
1. **User** - Admin authentication
2. **Berita** - News articles with image upload support
3. **Komentar** - Comments on news articles
4. **Dokter** - Doctor profiles with schedule and photo upload
5. **JanjiTemu** - Appointment bookings
6. **Gallery** - Photo galleries with main image and thumbnail
7. **GalleryImage** - Individual images in galleries with thumbnails
8. **Video** - Video content with thumbnails

**Documentation**: https://flask-sqlalchemy.palletsprojects.com/

---

## Authentication

### **Flask-Login** (User Session Management)
- **Version**: Latest
- **Purpose**: Handle user authentication and session management
- **Description**: Flask-Login provides user session management for Flask. It handles the common tasks of logging in, logging out, and remembering users' sessions.
- **Features**:
  - Login/Logout functionality
  - Session management
  - User authentication
  - Remember me functionality
  - Protected routes with `@login_required` decorator
- **Security**: Uses `@login_required` decorator to protect admin routes

**Documentation**: https://flask-login.readthedocs.io/

### **Werkzeug** (Security Utilities)
- **Version**: Latest (comes with Flask)
- **Purpose**: Password hashing and file security
- **Security Features Used**:
  - `generate_password_hash()` - Secure password hashing with PBKDF2-SHA256
  - `check_password_hash()` - Password verification
  - `secure_filename()` - Sanitize uploaded filenames to prevent directory traversal attacks

**Documentation**: https://werkzeug.palletsprojects.com/

---

## File Management

### **File Upload System**
- **Purpose**: Secure file upload and management for images
- **Supported Formats**: JPEG, JPG, PNG only
- **Maximum File Size**: 5 MB (5,242,880 bytes)
- **Storage Location**: `/static/uploads/`
- **Subdirectories**:
  - `/uploads/berita/` - News article images
  - `/uploads/dokter/` - Doctor profile photos
  - `/uploads/gallery/` - Gallery images and thumbnails

### **Pillow (PIL)** (Image Processing Library)
- **Version**: Latest
- **Purpose**: Image manipulation and thumbnail generation
- **Description**: Pillow is the Python Imaging Library that adds image processing capabilities to your Python interpreter.
- **Features Used**:
  - Image opening and loading
  - Thumbnail generation (300x300 pixels)
  - Image resizing with LANCZOS resampling (high quality)
  - Format conversion and optimization
  - Quality control (85% JPEG quality)
- **Thumbnail Generation**:
  - Automatic thumbnail creation for all uploaded images
  - Size: 300x300 pixels (maintains aspect ratio)
  - Naming: `{original_name}_thumb.{ext}`
  - Quality: 85% for optimal size/quality balance

**Documentation**: https://pillow.readthedocs.io/

### **File Security Features**:
1. **Extension Validation**: Only allows .png, .jpg, .jpeg files
2. **Size Validation**: Enforces 5MB maximum file size
3. **Filename Sanitization**: Uses `secure_filename()` to prevent attacks
4. **Unique Filenames**: Uses UUID4 to generate unique filenames and prevent collisions
5. **Automatic Directory Creation**: Creates subdirectories if they don't exist
6. **File Deletion**: Removes old files when updating or deleting records

**File Upload Workflow**:
```
1. User selects file → 
2. Validate extension (png/jpg/jpeg) → 
3. Validate size (max 5MB) → 
4. Sanitize filename → 
5. Generate unique filename with UUID → 
6. Save file to uploads folder → 
7. Create thumbnail (for gallery images) → 
8. Store file path in database → 
9. Serve via Flask static files
```

---

## Frontend

### **Jinja2** (Template Engine)
- **Version**: Latest (comes with Flask)
- **Purpose**: Dynamic HTML rendering
- **Description**: Jinja2 is a modern and designer-friendly templating language for Python, modeled after Django's templates.
- **Features Used**:
  - Template inheritance (`{% extends %}`)
  - Variable interpolation (`{{ variable }}`)
  - Control structures (`{% if %}`, `{% for %}`)
  - URL generation (`{{ url_for() }}`)
  - Static file serving
  - Flash message display

**Documentation**: https://jinja.palletsprojects.com/

### **Tailwind CSS** (Utility-First CSS Framework)
- **Version**: CDN version
- **Purpose**: Styling and responsive design
- **Description**: Tailwind CSS is a utility-first CSS framework that provides low-level utility classes to build custom designs.
- **Features Used**:
  - Responsive grid system
  - Dark mode support
  - Flexbox utilities
  - Color schemes
  - Typography
  - Forms styling
  - Transitions and animations
- **Custom Configuration**: `tailwind.config.js` included in templates folder

**Documentation**: https://tailwindcss.com/

### **JavaScript**
- **Purpose**: Interactive UI elements
- **Features**:
  - Dark mode toggle
  - Mobile navigation menu
  - Form validation
  - Scroll animations
  - AI chatbot interface

---

## AI Integration

### **OpenRouter API** (AI Chat Service)
- **Purpose**: Virtual assistant chatbot ("Kak Yor")
- **Model Used**: `tngtech/deepseek-r1t2-chimera:free`
- **Description**: OpenRouter provides access to various LLM models through a unified API
- **Features**:
  - Natural language processing
  - Hospital information assistance
  - Doctor schedule queries
  - Service information
  - Appointment guidance
- **API Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Integration**: RESTful API calls using Python `requests` library

### **Requests** (HTTP Library)
- **Version**: Latest
- **Purpose**: Make HTTP requests to external APIs
- **Description**: Requests is an elegant and simple HTTP library for Python
- **Used For**:
  - OpenRouter API calls
  - Error handling
  - Timeout management (30 seconds)
  - JSON response parsing

**Documentation**: https://requests.readthedocs.io/

---

## Deployment

### **Development Server**
- **Built-in Flask Development Server**
- **Host**: `localhost` (127.0.0.1)
- **Port**: 5000 (default)
- **Debug Mode**: Enabled (development only)
- **Auto-reload**: Enabled

### **Production Recommendations**:
1. **WSGI Server**: Use Gunicorn or uWSGI instead of Flask's development server
2. **Web Server**: Nginx or Apache as reverse proxy
3. **Database**: Consider PostgreSQL or MySQL for production
4. **Environment Variables**: Move sensitive configs to environment variables
5. **HTTPS**: Enable SSL/TLS certificates
6. **File Storage**: Consider cloud storage (AWS S3, Cloudinary) for uploaded files
7. **Monitoring**: Add logging and error tracking (Sentry)
8. **Caching**: Implement Redis or Memcached
9. **Static Files**: Serve static files via CDN

---

## Project Structure

```
Company-Profile---DKT-Slamet-Riyadi/
│
├── main.py                    # Main application file
├── requirements.txt           # Python dependencies
├── TECH_STACK.md             # This documentation
│
├── instance/
│   └── rst_slamet_riyadi.db  # SQLite database file
│
├── static/
│   ├── animation.css         # Custom animations
│   └── uploads/              # Uploaded files directory
│       ├── berita/           # News images
│       ├── dokter/           # Doctor photos
│       └── gallery/          # Gallery images & thumbnails
│
└── templates/                # HTML templates (Jinja2)
    ├── base.html             # Base template
    ├── index.html            # Homepage
    ├── berita.html           # News list
    ├── detail_berita.html    # News detail
    ├── tambah_berita.html    # Add news (admin)
    ├── jadwal.html           # Doctor schedules
    ├── tambah_dokter.html    # Add doctor (admin)
    ├── edit_dokter.html      # Edit doctor (admin)
    ├── buat_janji.html       # Appointment booking
    ├── galeri.html           # Gallery & videos
    ├── detail_galeri.html    # Gallery detail
    ├── tambah_galeri.html    # Add gallery (admin)
    ├── edit_galeri.html      # Edit gallery (admin)
    ├── tambah_gambar_galeri.html  # Add images to gallery
    ├── edit_gambar.html      # Edit gallery image
    ├── tambah_video.html     # Add video (admin)
    ├── edit_video.html       # Edit video (admin)
    ├── detail_video.html     # Video detail
    ├── login.html            # Admin login
    ├── register.html         # Admin registration
    └── tailwind.config.js    # Tailwind configuration
```

---

## Installation & Setup

### **Prerequisites**:
- Python 3.8 or higher
- pip (Python package installer)

### **Installation Steps**:

```bash
# 1. Clone or download the project
cd Company-Profile---DKT-Slamet-Riyadi

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python main.py

# 6. Access the website
# Open browser and navigate to: http://localhost:5000
```

### **First Time Setup**:
1. Database and tables will be created automatically on first run
2. Register an admin account at `/register`
3. Login with your admin credentials at `/login`
4. Start adding content (doctors, news, galleries)

---

## File Upload Configuration

### **Maximum File Size**: 5 MB
- Configured via `app.config['MAX_CONTENT_LENGTH']`
- Flask will automatically reject files larger than 5MB
- Returns HTTP 413 (Request Entity Too Large) error

### **Allowed Extensions**: PNG, JPG, JPEG
- Validated in `allowed_file()` function
- Case-insensitive check
- Only image formats allowed

### **Unique Filename Generation**:
```python
import uuid
unique_filename = f"{uuid.uuid4().hex}_{secure_filename(original_filename)}"
```
- Uses UUID4 (universally unique identifier)
- Prevents filename collisions
- Maintains original extension

### **Thumbnail Generation**:
- Size: 300x300 pixels
- Method: LANCZOS resampling (highest quality)
- Format: Same as original (PNG/JPG/JPEG)
- Quality: 85% (for JPEG)
- Naming: `{name}_thumb.{ext}`

---

## Security Best Practices Implemented

1. **Password Security**:
   - PBKDF2-SHA256 hashing algorithm
   - Salt automatically generated by Werkzeug
   - Passwords never stored in plain text

2. **File Upload Security**:
   - Extension whitelist (only png, jpg, jpeg)
   - Filename sanitization via `secure_filename()`
   - Unique filenames to prevent overwrites
   - Size limit enforcement (5MB)
   - Files stored outside web root when possible

3. **SQL Injection Prevention**:
   - SQLAlchemy ORM parameterized queries
   - No raw SQL string concatenation

4. **Authentication**:
   - Login required for admin functions
   - Session-based authentication
   - Flask-Login handles session security

5. **XSS Prevention**:
   - Jinja2 auto-escapes template variables
   - User input sanitized before database storage

---

## API Endpoints

### **Public Routes**:
- `GET /` - Homepage
- `GET /berita_acara` - News list
- `GET /berita/<id>` - News detail
- `POST /berita/<id>` - Add comment
- `GET /jadwal_dokter` - Doctor schedules
- `GET /buat_janji` - Appointment form
- `POST /buat_janji` - Submit appointment
- `GET /galeri` - Gallery & videos
- `GET /galeri/<id>` - Gallery detail
- `GET /video/<id>` - Video detail
- `POST /chat` - AI chatbot (JSON API)

### **Admin Routes** (Login Required):
- `GET/POST /login` - Admin login
- `GET/POST /register` - Admin registration
- `GET /logout` - Logout
- `GET/POST /tambah_berita` - Add news (with file upload)
- `GET/POST /tambah_dokter` - Add doctor (with file upload)
- `GET/POST /edit_dokter/<id>` - Edit doctor (with file upload)
- `POST /hapus_dokter/<id>` - Delete doctor
- `GET/POST /tambah_galeri` - Add gallery (with file upload)
- `GET/POST /edit_galeri/<id>` - Edit gallery (with file upload)
- `POST /hapus_galeri/<id>` - Delete gallery
- `GET/POST /galeri/<id>/tambah_gambar` - Add image to gallery (with file upload)
- `GET/POST /edit_gambar/<id>` - Edit gallery image (with file upload)
- `POST /hapus_gambar/<id>` - Delete gallery image
- `GET/POST /tambah_video` - Add video
- `GET/POST /edit_video/<id>` - Edit video
- `POST /hapus_video/<id>` - Delete video

---

## Database Schema

### **User Table**:
```
- id (Integer, Primary Key)
- username (String(150), Unique, Not Null)
- password (String(150), Not Null) [Hashed]
```

### **Berita Table**:
```
- id (Integer, Primary Key)
- judul (String(200), Not Null)
- konten (Text, Not Null)
- tanggal (DateTime, Default: UTC Now)
- gambar (String(300), Nullable) [File path]
- komentar (Relationship to Komentar)
```

### **Komentar Table**:
```
- id (Integer, Primary Key)
- nama_pengirim (String(100), Not Null)
- isi_komentar (Text, Not Null)
- tanggal (DateTime, Default: UTC Now)
- berita_id (Integer, Foreign Key to Berita)
```

### **Dokter Table**:
```
- id (Integer, Primary Key)
- nama (String(150), Not Null)
- spesialis (String(150), Not Null)
- jadwal (String(200), Not Null)
- foto (String(300), Nullable) [File path]
- janji_temu (Relationship to JanjiTemu)
```

### **JanjiTemu Table**:
```
- id (Integer, Primary Key)
- nama_pasien (String(150), Not Null)
- no_hp (String(20), Not Null)
- keluhan (Text, Not Null)
- tanggal_rencana (String(50), Not Null)
- dokter_id (Integer, Foreign Key to Dokter)
- status (String(50), Default: 'Menunggu Konfirmasi')
```

### **Gallery Table**:
```
- id (Integer, Primary Key)
- title (String(200), Not Null)
- main_image (String(300), Not Null) [File path]
- thumbnail (String(300), Nullable) [File path]
- created_at (DateTime, Default: UTC Now)
- images (Relationship to GalleryImage, Cascade Delete)
```

### **GalleryImage Table**:
```
- id (Integer, Primary Key)
- subtitle (String(200), Not Null)
- image_url (String(300), Not Null) [File path]
- thumbnail (String(300), Nullable) [File path]
- gallery_id (Integer, Foreign Key to Gallery)
- created_at (DateTime, Default: UTC Now)
```

### **Video Table**:
```
- id (Integer, Primary Key)
- title (String(200), Not Null)
- description (Text, Nullable)
- video_url (String(500), Not Null)
- thumbnail_url (String(500), Nullable)
- created_at (DateTime, Default: UTC Now)
```

---

## Environment Configuration

### **Development Config** (main.py):
```python
app.config['SECRET_KEY'] = 'rahasia-negara-aman-123'  # Change in production!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rst_slamet_riyadi.db'
app.config['OPENROUTER_API_KEY'] = '-'  # Add your API key
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
```

### **Production Recommendations**:
```python
# Use environment variables for sensitive data
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['OPENROUTER_API_KEY'] = os.environ.get('OPENROUTER_API_KEY')
```

---

## Support & Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Pillow Documentation**: https://pillow.readthedocs.io/
- **Tailwind CSS Documentation**: https://tailwindcss.com/docs
- **Python Documentation**: https://docs.python.org/3/

---

## Version History

**Version 1.0** (Current)
- Initial release
- File upload system implemented
- Thumbnail generation
- Admin panel with edit capabilities
- AI chatbot integration
- Responsive design with dark mode

**Recent Updates** (February 2026)
- ✅ Added file upload support for images (max 5MB, PNG/JPG/JPEG only)
- ✅ Implemented automatic thumbnail generation
- ✅ Added edit functionality for doctor schedules
- ✅ Enhanced admin panel with file management
- ✅ Improved security with file validation
- ✅ Added support for image previews in edit forms

---

## License

This project is created for RST Slamet Riyadi educational purposes.

---

## Contact

For technical support or questions about this documentation, please contact the development team.

**Last Updated**: February 5, 2026
