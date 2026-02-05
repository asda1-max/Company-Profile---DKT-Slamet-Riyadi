# 🚀 Quick Start Guide

## Start the Application in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python main.py
```

### Step 3: Open Browser
```
http://localhost:5000
```

---

## First Time Setup

### 1. Create Admin Account
- Visit: `http://localhost:5000/register`
- Enter username and password
- Click "Register"

### 2. Login
- Visit: `http://localhost:5000/login`
- Enter your credentials
- Click "Login"

### 3. Start Adding Content

#### Add Doctor:
1. Go to "Jadwal Dokter"
2. Click "Tambah Dokter Baru"
3. Fill form and upload photo (PNG/JPG/JPEG, max 5MB)
4. Click "Simpan Data"

#### Add News:
1. Go to "Berita Acara"
2. Click "Tambah Berita Baru"
3. Fill form and upload image
4. Click "Terbitkan Berita"

#### Add Gallery:
1. Go to "Galeri"
2. Click "Tambah Foto"
3. Upload main image (thumbnail auto-generated)
4. Click "Simpan Galeri"
5. Click on gallery to add more images

---

## File Upload Rules

✅ **Allowed**: PNG, JPG, JPEG  
✅ **Max Size**: 5 MB  
✅ **Auto Feature**: Thumbnails created automatically  

---

## Common Tasks

### Edit Doctor Schedule
1. Login as admin
2. Go to "Jadwal Dokter"
3. Click "Edit" button on doctor card
4. Update information
5. Optionally upload new photo
6. Click "Simpan Perubahan"

### Delete Doctor
1. Login as admin
2. Go to "Jadwal Dokter"
3. Click "Hapus" button
4. Confirm deletion

### Add Images to Gallery
1. Open a gallery
2. Click "Tambah Gambar"
3. Upload image and add subtitle
4. Click "Tambah Gambar"

---

## Troubleshooting

### Port Already in Use
```bash
# Use different port
python main.py --port 5001
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Upload Failed
- Check file size (< 5MB)
- Check file format (PNG/JPG/JPEG only)
- Check folder permissions

---

## Documentation

📚 **Full Documentation**: See [TECH_STACK.md](TECH_STACK.md)  
📖 **README**: See [README.md](README.md)  
✅ **Implementation Details**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)  

---

## Support

For technical issues, check the documentation or contact support.

**Last Updated**: February 5, 2026
