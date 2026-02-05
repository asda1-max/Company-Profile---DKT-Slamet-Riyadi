# RST Slamet Riyadi - Company Profile Website

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-latest-red)
![License](https://img.shields.io/badge/license-Educational-yellow)

Sistem informasi profil perusahaan untuk RST Slamet Riyadi (Rumah Sakit Tentara Tingkat III Slamet Riyadi) dengan fitur manajemen berita, jadwal dokter, galeri foto, video, dan chatbot AI.

---

## 🚀 Fitur Utama

### 🔐 Admin Panel
- **Autentikasi**: Login/Register dengan password hashing (PBKDF2-SHA256)
- **Manajemen Berita**: Tambah, edit, hapus berita dengan upload gambar
- **Manajemen Dokter**: Tambah, edit, hapus data dokter dengan foto dan jadwal
- **Manajemen Galeri**: Tambah, edit, hapus galeri foto dengan thumbnail otomatis
- **Manajemen Video**: Tambah, edit, hapus video dengan thumbnail

### 📸 Upload File System
- **Format**: PNG, JPG, JPEG only
- **Ukuran Maksimal**: 5 MB per file
- **Keamanan**: 
  - Validasi ekstensi file
  - Sanitasi nama file
  - Unique filename dengan UUID
  - Thumbnail otomatis (300x300px)
- **Folder Terorganisir**:
  - `/static/uploads/berita/` - Gambar berita
  - `/static/uploads/dokter/` - Foto dokter
  - `/static/uploads/gallery/` - Galeri & thumbnail

### 👥 Fitur Publik
- **Homepage**: Profil rumah sakit, layanan, fasilitas
- **Berita**: Daftar berita dengan sistem komentar
- **Jadwal Dokter**: Lihat jadwal praktik dokter dan buat janji temu
- **Galeri**: Koleksi foto kegiatan rumah sakit
- **Video**: Dokumentasi video kegiatan
- **AI Chatbot**: Virtual assistant "Kak Yor" untuk informasi rumah sakit

### 🎨 Design Features
- **Responsive Design**: Mobile-friendly dengan Tailwind CSS
- **Dark Mode**: Toggle dark/light theme
- **Smooth Animations**: Scroll animations dan transitions
- **Modern UI**: Clean dan professional interface

---

## 📋 Requirements

### Software
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### Dependencies (requirements.txt)
```
flask
flask_sqlalchemy
flask_login
werkzeug
requests
pillow
```

---

## 🛠️ Instalasi

### 1. Clone atau Download Project
```bash
cd Company-Profile---DKT-Slamet-Riyadi
```

### 2. Buat Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi (Opsional)
Edit `main.py` untuk mengubah konfigurasi:
```python
# Secret Key (ganti untuk production!)
app.config['SECRET_KEY'] = 'rahasia-negara-aman-123'

# OpenRouter API Key untuk chatbot
app.config['OPENROUTER_API_KEY'] = '-'  # Masukkan API key Anda
```

### 5. Jalankan Aplikasi
```bash
python main.py
```

### 6. Akses Website
Buka browser dan navigasi ke:
```
http://localhost:5000
```

---

## 📝 Penggunaan

### Pertama Kali
1. **Register Admin**: Kunjungi `/register` untuk membuat akun admin
2. **Login**: Login di `/login` dengan kredensial yang dibuat
3. **Tambah Data**: Mulai menambahkan berita, dokter, galeri, dan video

### Upload File
1. **Login** sebagai admin
2. Pilih menu yang ingin ditambahkan (Berita, Dokter, atau Galeri)
3. Klik tombol **Upload/Pilih File**
4. Pilih gambar (PNG/JPG/JPEG, max 5MB)
5. Isi form dan klik **Simpan**

### Edit Data Dokter
1. **Login** sebagai admin
2. Buka halaman **Jadwal Dokter**
3. Klik tombol **Edit** pada kartu dokter
4. Ubah data yang diperlukan
5. Upload foto baru (opsional)
6. Klik **Simpan Perubahan**

### Manajemen Galeri
1. **Tambah Galeri**: Upload gambar utama (thumbnail otomatis dibuat)
2. **Tambah Gambar ke Galeri**: Upload lebih banyak foto ke galeri
3. **Edit**: Ubah judul atau gambar
4. **Hapus**: Hapus galeri atau gambar individual

---

## 📁 Struktur Project

```
Company-Profile---DKT-Slamet-Riyadi/
│
├── main.py                    # Main application file
├── requirements.txt           # Python dependencies
├── README.md                  # Dokumentasi ini
├── TECH_STACK.md             # Dokumentasi teknis lengkap
│
├── instance/
│   └── rst_slamet_riyadi.db  # SQLite database (auto-generated)
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

## 🔒 Keamanan

### Password
- Hash PBKDF2-SHA256 dengan salt otomatis
- Password tidak pernah disimpan dalam plain text

### File Upload
- ✅ Validasi ekstensi (hanya PNG, JPG, JPEG)
- ✅ Validasi ukuran (max 5MB)
- ✅ Sanitasi nama file dengan `secure_filename()`
- ✅ Unique filename dengan UUID4
- ✅ Perlindungan directory traversal

### Database
- ✅ SQLAlchemy ORM mencegah SQL injection
- ✅ Parameterized queries

### Authentication
- ✅ Login required untuk fungsi admin
- ✅ Session-based authentication
- ✅ Logout otomatis saat sesi berakhir

---

## 🎯 API Endpoints

### Public Routes
- `GET /` - Homepage
- `GET /berita_acara` - Daftar berita
- `GET /berita/<id>` - Detail berita
- `POST /berita/<id>` - Tambah komentar
- `GET /jadwal_dokter` - Jadwal dokter
- `GET /buat_janji` - Form janji temu
- `POST /buat_janji` - Submit janji temu
- `GET /galeri` - Galeri & video
- `GET /galeri/<id>` - Detail galeri
- `GET /video/<id>` - Detail video
- `POST /chat` - AI chatbot (JSON API)

### Admin Routes (Login Required)
- `GET/POST /login` - Login admin
- `GET/POST /register` - Register admin
- `GET /logout` - Logout
- `GET/POST /tambah_berita` - Tambah berita (dengan upload)
- `GET/POST /tambah_dokter` - Tambah dokter (dengan upload)
- `GET/POST /edit_dokter/<id>` - Edit dokter (dengan upload)
- `POST /hapus_dokter/<id>` - Hapus dokter
- `GET/POST /tambah_galeri` - Tambah galeri (dengan upload)
- `GET/POST /edit_galeri/<id>` - Edit galeri (dengan upload)
- `POST /hapus_galeri/<id>` - Hapus galeri
- Dan lainnya...

---

## 💾 Database Schema

### User
- id, username (unique), password (hashed)

### Berita
- id, judul, konten, tanggal, gambar (file path)
- Relasi: komentar (one-to-many)

### Komentar
- id, nama_pengirim, isi_komentar, tanggal, berita_id

### Dokter
- id, nama, spesialis, jadwal, foto (file path)
- Relasi: janji_temu (one-to-many)

### JanjiTemu
- id, nama_pasien, no_hp, keluhan, tanggal_rencana, dokter_id, status

### Gallery
- id, title, main_image (file path), thumbnail (file path), created_at
- Relasi: images (one-to-many, cascade delete)

### GalleryImage
- id, subtitle, image_url (file path), thumbnail (file path), gallery_id, created_at

### Video
- id, title, description, video_url, thumbnail_url, created_at

---

## 🚀 Deployment (Production)

### Recommendations:
1. **WSGI Server**: Gunakan Gunicorn atau uWSGI
   ```bash
   pip install gunicorn
   gunicorn -w 4 main:app
   ```

2. **Web Server**: Nginx atau Apache sebagai reverse proxy

3. **Database**: PostgreSQL atau MySQL untuk production
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/dbname'
   ```

4. **Environment Variables**: Simpan sensitive data di env
   ```python
   import os
   app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
   app.config['OPENROUTER_API_KEY'] = os.environ.get('OPENROUTER_API_KEY')
   ```

5. **HTTPS**: Enable SSL/TLS certificates (Let's Encrypt)

6. **File Storage**: Cloud storage (AWS S3, Cloudinary) untuk file upload

7. **Monitoring**: Logging dan error tracking (Sentry)

---

## 🛠️ Troubleshooting

### Error: "Address already in use"
```bash
# Port 5000 sudah digunakan, ganti port
flask run --port 5001
```

### Error: "No module named 'flask'"
```bash
# Install dependencies
pip install -r requirements.txt
```

### Error: Upload file gagal
- Pastikan ukuran file < 5MB
- Pastikan format PNG, JPG, atau JPEG
- Pastikan folder `static/uploads/` ada dan writable

### Database error
```bash
# Hapus database dan buat ulang
rm instance/rst_slamet_riyadi.db
python main.py
```

---

## 📚 Dokumentasi Lengkap

Untuk dokumentasi teknis lengkap tentang tech stack yang digunakan, baca:
- **[TECH_STACK.md](TECH_STACK.md)** - Dokumentasi lengkap semua teknologi

---

## 📞 Kontak & Support

- **Email**: admin@rstslamentriyadi.com
- **Website**: https://rstslamentriyadi.com
- **Lokasi**: Jl. Brigjend Slamet Riyadi No. 321, Surakarta

---

## 📝 Version History

**Version 1.0** (February 2026)
- ✅ Initial release
- ✅ File upload system implemented
- ✅ Thumbnail generation
- ✅ Admin panel with edit capabilities
- ✅ AI chatbot integration
- ✅ Responsive design with dark mode

**Recent Updates**:
- ✅ Added file upload support for images (max 5MB, PNG/JPG/JPEG)
- ✅ Implemented automatic thumbnail generation
- ✅ Added edit functionality for doctor schedules
- ✅ Enhanced admin panel with file management
- ✅ Improved security with file validation

---

## 📄 License

Project ini dibuat untuk tujuan edukasi dan pembelajaran untuk RST Slamet Riyadi.

---

## 🙏 Credits

- **Framework**: Flask (Python)
- **Database**: SQLAlchemy + SQLite
- **CSS**: Tailwind CSS
- **Icons**: Heroicons
- **Image Processing**: Pillow (PIL)
- **AI**: OpenRouter API

---

**Last Updated**: February 5, 2026
