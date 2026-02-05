import os
import uuid
import requests
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rahasia-negara-aman-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rst_slamet_riyadi.db'
app.config['OPENROUTER_API_KEY'] = "-"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ================= MODELS =================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relasi ke Berita
    berita = db.relationship('Berita', backref='category', lazy=True)

class Berita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    konten = db.Column(db.Text, nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    gambar = db.Column(db.String(300), nullable=True)  # Stores file path
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    # Relasi ke Komentar
    komentar = db.relationship('Komentar', backref='berita', lazy=True)

class Komentar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_pengirim = db.Column(db.String(100), nullable=False)
    isi_komentar = db.Column(db.Text, nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    berita_id = db.Column(db.Integer, db.ForeignKey('berita.id'), nullable=False)

class Dokter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
    spesialis = db.Column(db.String(150), nullable=False)
    jadwal = db.Column(db.String(200), nullable=False)
    foto = db.Column(db.String(300), nullable=True)  # Stores file path
    # Relasi ke Janji Temu
    janji_temu = db.relationship('JanjiTemu', backref='dokter', lazy=True)

class JanjiTemu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_pasien = db.Column(db.String(150), nullable=False)
    no_hp = db.Column(db.String(20), nullable=False)
    keluhan = db.Column(db.Text, nullable=False)
    tanggal_rencana = db.Column(db.String(50), nullable=False) # Simplifikasi format tanggal
    dokter_id = db.Column(db.Integer, db.ForeignKey('dokter.id'), nullable=False)
    status = db.Column(db.String(50), default='Menunggu Konfirmasi')

class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    main_image = db.Column(db.String(300), nullable=False)  # Stores file path
    thumbnail = db.Column(db.String(300), nullable=True)  # Stores thumbnail file path
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relasi ke GalleryImage
    images = db.relationship('GalleryImage', backref='gallery', lazy=True, cascade='all, delete-orphan')

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subtitle = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)  # Stores file path
    thumbnail = db.Column(db.String(300), nullable=True)  # Stores thumbnail file path
    gallery_id = db.Column(db.Integer, db.ForeignKey('gallery.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= HELPER FUNCTIONS =================

def allowed_file(filename):
    """Check if file extension is allowed (png, jpg, jpeg)"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_image(file, folder='general'):
    """
    Save uploaded image file with unique filename
    Args:
        file: FileStorage object from request.files
        folder: subfolder within uploads directory (default: 'general')
    Returns:
        relative path to saved file or None if error
    """
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Create folder if not exists
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # Return relative path from static folder
        return os.path.join('uploads', folder, unique_filename).replace('\\', '/')
    return None

def create_thumbnail(image_path, folder='general', size=(300, 300)):
    """
    Create thumbnail from uploaded image
    Args:
        image_path: relative path to the original image
        folder: subfolder within uploads directory
        size: thumbnail size tuple (width, height)
    Returns:
        relative path to thumbnail or None if error
    """
    try:
        # Get full path to original image
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, os.path.basename(image_path))
        
        # Open and resize image
        img = Image.open(full_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Generate thumbnail filename
        basename = os.path.basename(image_path)
        name, ext = os.path.splitext(basename)
        thumbnail_filename = f"{name}_thumb{ext}"
        
        # Save thumbnail
        thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, thumbnail_filename)
        img.save(thumbnail_path, quality=85)
        
        # Return relative path from static folder
        return os.path.join('uploads', folder, thumbnail_filename).replace('\\', '/')
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return None

def delete_image(image_path):
    """Delete image file from filesystem"""
    if image_path:
        try:
            full_path = os.path.join('static', image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"Error deleting image: {e}")

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ================= ROUTES UTAMA =================

@app.route("/")
def index():
    # Find the Fasilitas Rumah Sakit gallery
    fasilitas_gallery = Gallery.query.filter_by(title="Fasilitas Rumah Sakit").first()
    fasilitas_gallery_id = fasilitas_gallery.id if fasilitas_gallery else None
    return render_template("index.html", fasilitas_gallery_id=fasilitas_gallery_id)

# --- BERITA & KOMENTAR ---

@app.route("/berita_acara")
def berita_acara():
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('search', '').strip()
    
    # Build query
    query = Berita.query
    
    # Apply category filter
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Apply search filter
    if search_query:
        query = query.filter(Berita.judul.contains(search_query))
    
    # Get filtered berita
    daftar_berita = query.order_by(Berita.tanggal.desc()).all()
    
    # Get all categories for filter
    categories = Category.query.order_by(Category.name).all()
    
    return render_template("berita.html", berita=daftar_berita, categories=categories, 
                         selected_category=category_id, search_query=search_query)

@app.route("/berita/<int:id>", methods=['GET', 'POST'])
def detail_berita(id):
    berita_item = Berita.query.get_or_404(id)
    
    # Logic Tambah Komentar (User)
    if request.method == 'POST':
        nama = request.form.get('nama')
        isi = request.form.get('isi')
        
        komentar_baru = Komentar(nama_pengirim=nama, isi_komentar=isi, berita_id=id)
        db.session.add(komentar_baru)
        db.session.commit()
        flash('Komentar berhasil dikirim!', 'success')
        return redirect(url_for('detail_berita', id=id))

    return render_template("detail_berita.html", berita=berita_item)

@app.route("/tambah_berita", methods=['GET', 'POST'])
@login_required
def tambah_berita():
    if request.method == 'POST':
        judul = request.form.get('judul')
        konten = request.form.get('konten')
        category_id = request.form.get('category_id')
        new_category = request.form.get('new_category', '').strip()
        
        # Handle new category creation
        if new_category:
            # Create slug from name
            slug = new_category.lower().replace(' ', '-')
            # Check if category already exists
            existing = Category.query.filter_by(slug=slug).first()
            if existing:
                category_id = existing.id
            else:
                new_cat = Category(name=new_category, slug=slug)
                db.session.add(new_cat)
                db.session.flush()  # Get the ID before commit
                category_id = new_cat.id
        
        # Handle image - check both inputs
        gambar_path = None
        has_file = 'gambar_file' in request.files and request.files['gambar_file'].filename != ''
        has_url = request.form.get('gambar_url', '').strip() != ''
        
        # Validation: only one method allowed
        if has_file and has_url:
            flash('Pilih hanya satu: Upload file ATAU masukkan URL, bukan keduanya!', 'warning')
            return redirect(url_for('tambah_berita'))
        
        if has_file:
            file = request.files['gambar_file']
            gambar_path = save_image(file, folder='berita')
            if not gambar_path:
                flash('Format gambar tidak valid. Gunakan PNG, JPG, atau JPEG (max 5MB)', 'warning')
                return redirect(url_for('tambah_berita'))
        elif has_url:
            gambar_path = request.form.get('gambar_url')
        
        berita_baru = Berita(judul=judul, konten=konten, gambar=gambar_path, 
                           category_id=int(category_id) if category_id else None)
        db.session.add(berita_baru)
        db.session.commit()
        flash('Berita berhasil diterbitkan!', 'success')
        return redirect(url_for('berita_acara'))
    
    # GET request - load categories
    categories = Category.query.order_by(Category.name).all()
    return render_template("tambah_berita.html", categories=categories)

# --- DOKTER & JANJI TEMU ---

@app.route("/jadwal_dokter")
def jadwal_dokter():
    daftar_dokter = Dokter.query.all()
    return render_template("jadwal.html", dokter=daftar_dokter)

@app.route("/tambah_dokter", methods=['GET', 'POST'])
@login_required
def tambah_dokter():
    if request.method == 'POST':
        nama = request.form.get('nama')
        spesialis = request.form.get('spesialis')
        jadwal = request.form.get('jadwal')
        
        # Handle image - check both inputs
        foto_path = None
        has_file = 'foto_file' in request.files and request.files['foto_file'].filename != ''
        has_url = request.form.get('foto_url', '').strip() != ''
        
        # Validation: only one method allowed
        if has_file and has_url:
            flash('Pilih hanya satu: Upload file ATAU masukkan URL, bukan keduanya!', 'warning')
            return redirect(url_for('tambah_dokter'))
        
        if has_file:
            file = request.files['foto_file']
            foto_path = save_image(file, folder='dokter')
            if not foto_path:
                flash('Format foto tidak valid. Gunakan PNG, JPG, atau JPEG (max 5MB)', 'warning')
                return redirect(url_for('tambah_dokter'))
        elif has_url:
            foto_path = request.form.get('foto_url')
        
        dokter_baru = Dokter(nama=nama, spesialis=spesialis, jadwal=jadwal, foto=foto_path)
        db.session.add(dokter_baru)
        db.session.commit()
        flash('Data Dokter berhasil ditambahkan!', 'success')
        return redirect(url_for('jadwal_dokter'))
        
    return render_template("tambah_dokter.html")

@app.route("/edit_dokter/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_dokter(id):
    dokter = Dokter.query.get_or_404(id)
    
    if request.method == 'POST':
        dokter.nama = request.form.get('nama')
        dokter.spesialis = request.form.get('spesialis')
        dokter.jadwal = request.form.get('jadwal')
        
        # Handle image - check both inputs
        new_foto = None
        has_file = 'foto_file' in request.files and request.files['foto_file'].filename != ''
        has_url = request.form.get('foto_url', '').strip() != ''
        
        # Validation: only one method allowed
        if has_file and has_url:
            flash('Pilih hanya satu: Upload file ATAU masukkan URL, bukan keduanya!', 'warning')
            return redirect(url_for('edit_dokter', id=id))
        
        if has_file:
            file = request.files['foto_file']
            new_foto = save_image(file, folder='dokter')
            if not new_foto:
                flash('Format foto tidak valid. Gunakan PNG, JPG, atau JPEG (max 5MB)', 'warning')
                return redirect(url_for('edit_dokter', id=id))
        elif has_url:
            new_foto = request.form.get('foto_url')
        
        # Update foto if new one provided
        if new_foto:
            # Delete old image file if it was uploaded (not URL)
            if dokter.foto and not dokter.foto.startswith('http'):
                delete_image(dokter.foto)
            dokter.foto = new_foto
        
        db.session.commit()
        flash('Data Dokter berhasil diperbarui!', 'success')
        return redirect(url_for('jadwal_dokter'))
    
    return render_template("edit_dokter.html", dokter=dokter)

@app.route("/hapus_dokter/<int:id>", methods=['POST'])
@login_required
def hapus_dokter(id):
    dokter = Dokter.query.get_or_404(id)
    
    # Delete all appointments related to this doctor first
    JanjiTemu.query.filter_by(dokter_id=id).delete()
    
    # Delete image file if exists
    if dokter.foto:
        delete_image(dokter.foto)
    
    db.session.delete(dokter)
    db.session.commit()
    flash('Data Dokter berhasil dihapus!', 'success')
    return redirect(url_for('jadwal_dokter'))

@app.route("/buat_janji", methods=['GET', 'POST'])
def buat_janji():
    if request.method == 'POST':
        nama_pasien = request.form.get('nama_pasien')
        no_hp = request.form.get('no_hp')
        keluhan = request.form.get('keluhan')
        dokter_id = request.form.get('dokter_id')
        tanggal = request.form.get('tanggal')
        
        janji_baru = JanjiTemu(
            nama_pasien=nama_pasien, 
            no_hp=no_hp, 
            keluhan=keluhan, 
            dokter_id=dokter_id,
            tanggal_rencana=tanggal
        )
        db.session.add(janji_baru)
        db.session.commit()
        
        # Redirect to confirmation page with appointment ID
        return redirect(url_for('konfirmasi_janji', id=janji_baru.id))
    
    # Jika GET, ambil id dokter dari query param (jika ada) untuk auto-select
    selected_dokter_id = request.args.get('dokter_id')
    daftar_dokter = Dokter.query.all()
    return render_template("buat_janji.html", dokter=daftar_dokter, selected_id=selected_dokter_id)

@app.route("/konfirmasi_janji/<int:id>")
def konfirmasi_janji(id):
    janji = JanjiTemu.query.get_or_404(id)
    return render_template("konfirmasi_janji.html", janji=janji)

@app.route("/permintaan")
@login_required
def permintaan():
    # Admin view - all appointment requests
    daftar_janji = JanjiTemu.query.order_by(JanjiTemu.id.desc()).all()
    return render_template("permintaan.html", janji_list=daftar_janji)

@app.route("/riwayat")
def riwayat():
    # User view - search appointments by phone number
    no_hp = request.args.get('no_hp', '').strip()
    janji_list = []
    
    if no_hp:
        janji_list = JanjiTemu.query.filter_by(no_hp=no_hp).order_by(JanjiTemu.id.desc()).all()
    
    return render_template("riwayat.html", janji_list=janji_list, no_hp=no_hp)

@app.route("/update_status_janji/<int:id>/<status>")
@login_required
def update_status_janji(id, status):
    janji = JanjiTemu.query.get_or_404(id)
    janji.status = status
    db.session.commit()
    flash(f'Status janji temu berhasil diubah menjadi "{status}"!', 'success')
    return redirect(url_for('permintaan'))

# --- GALERI ---

@app.route("/galeri")
def galeri():
    galleries = Gallery.query.order_by(Gallery.created_at.desc()).all()
    videos = Video.query.order_by(Video.created_at.desc()).all()
    return render_template("galeri.html", galleries=galleries, videos=videos)

@app.route("/galeri/<int:id>")
def detail_galeri(id):
    gallery_item = Gallery.query.get_or_404(id)
    return render_template("detail_galeri.html", gallery=gallery_item)

@app.route("/tambah_galeri", methods=['GET', 'POST'])
@login_required
def tambah_galeri():
    if request.method == 'POST':
        title = request.form.get('title')
        
        # Handle main image - check both inputs
        main_image_path = None
        thumbnail_path = None
        has_file = 'main_image_file' in request.files and request.files['main_image_file'].filename != ''
        has_url = request.form.get('main_image_url', '').strip() != ''
        
        # Validation: only one method allowed
        if has_file and has_url:
            flash('Pilih hanya satu: Upload file ATAU masukkan URL, bukan keduanya!', 'warning')
            return redirect(url_for('tambah_galeri'))
        
        if has_file:
            file = request.files['main_image_file']
            main_image_path = save_image(file, folder='gallery')
            if not main_image_path:
                flash('Format gambar tidak valid. Gunakan PNG, JPG, atau JPEG (max 5MB)', 'warning')
                return redirect(url_for('tambah_galeri'))
            # Create thumbnail only for uploaded files
            thumbnail_path = create_thumbnail(main_image_path, folder='gallery')
        elif has_url:
            main_image_path = request.form.get('main_image_url')
        
        if not main_image_path:
            flash('Gambar utama wajib diisi (upload file atau URL)!', 'warning')
            return redirect(url_for('tambah_galeri'))
        
        gallery_baru = Gallery(title=title, main_image=main_image_path, thumbnail=thumbnail_path)
        db.session.add(gallery_baru)
        db.session.commit()
        flash('Gallery berhasil ditambahkan!', 'success')
        return redirect(url_for('detail_galeri', id=gallery_baru.id))
        
    return render_template("tambah_galeri.html")

@app.route("/galeri/<int:gallery_id>/tambah_gambar", methods=['GET', 'POST'])
@login_required
def tambah_gambar_galeri(gallery_id):
    gallery = Gallery.query.get_or_404(gallery_id)
    
    if request.method == 'POST':
        subtitle = request.form.get('subtitle')
        
        # Handle image - check both inputs
        image_path = None
        thumbnail_path = None
        has_file = 'image_file' in request.files and request.files['image_file'].filename != ''
        has_url = request.form.get('image_url_input', '').strip() != ''
        
        # Validation: only one method allowed
        if has_file and has_url:
            flash('Pilih hanya satu: Upload file ATAU masukkan URL, bukan keduanya!', 'warning')
            return redirect(url_for('tambah_gambar_galeri', gallery_id=gallery_id))
        
        if has_file:
            file = request.files['image_file']
            image_path = save_image(file, folder='gallery')
            if not image_path:
                flash('Format gambar tidak valid. Gunakan PNG, JPG, atau JPEG (max 5MB)', 'warning')
                return redirect(url_for('tambah_gambar_galeri', gallery_id=gallery_id))
            # Create thumbnail only for uploaded files
            thumbnail_path = create_thumbnail(image_path, folder='gallery')
        elif has_url:
            image_path = request.form.get('image_url_input')
        
        if not image_path:
            flash('Gambar wajib diisi (upload file atau URL)!', 'warning')
            return redirect(url_for('tambah_gambar_galeri', gallery_id=gallery_id))
        
        gambar_baru = GalleryImage(subtitle=subtitle, image_url=image_path, thumbnail=thumbnail_path, gallery_id=gallery_id)
        db.session.add(gambar_baru)
        db.session.commit()
        flash('Gambar berhasil ditambahkan ke gallery!', 'success')
        return redirect(url_for('detail_galeri', id=gallery_id))
        
    return render_template("tambah_gambar_galeri.html", gallery=gallery)

@app.route("/edit_galeri/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_galeri(id):
    gallery = Gallery.query.get_or_404(id)
    
    if request.method == 'POST':
        gallery.title = request.form.get('title')
        
        # Handle image - check both inputs
        new_image = None
        new_thumbnail = None
        has_file = 'main_image_file' in request.files and request.files['main_image_file'].filename != ''
        has_url = request.form.get('main_image_url', '').strip() != ''
        
        # Validation: only one method allowed
        if has_file and has_url:
            flash('Pilih hanya satu: Upload file ATAU masukkan URL, bukan keduanya!', 'warning')
            return redirect(url_for('edit_galeri', id=id))
        
        if has_file:
            file = request.files['main_image_file']
            new_image = save_image(file, folder='gallery')
            if not new_image:
                flash('Format gambar tidak valid. Gunakan PNG, JPG, atau JPEG (max 5MB)', 'warning')
                return redirect(url_for('edit_galeri', id=id))
            # Create thumbnail for uploaded file
            new_thumbnail = create_thumbnail(new_image, folder='gallery')
        elif has_url:
            new_image = request.form.get('main_image_url')
            new_thumbnail = None  # No thumbnail for URLs
        
        # Update image if new one provided
        if new_image:
            # Delete old image files if they were uploaded (not URLs)
            if gallery.main_image and not gallery.main_image.startswith('http'):
                delete_image(gallery.main_image)
            if gallery.thumbnail and not gallery.thumbnail.startswith('http'):
                delete_image(gallery.thumbnail)
            
            gallery.main_image = new_image
            gallery.thumbnail = new_thumbnail
        
        db.session.commit()
        flash('Gallery berhasil diperbarui!', 'success')
        return redirect(url_for('detail_galeri', id=id))
    
    return render_template("edit_galeri.html", gallery=gallery)

@app.route("/hapus_galeri/<int:id>", methods=['POST'])
@login_required
def hapus_galeri(id):
    gallery = Gallery.query.get_or_404(id)
    
    # Delete all associated images
    if gallery.main_image:
        delete_image(gallery.main_image)
    if gallery.thumbnail:
        delete_image(gallery.thumbnail)
    
    for img in gallery.images:
        if img.image_url:
            delete_image(img.image_url)
        if img.thumbnail:
            delete_image(img.thumbnail)
    
    db.session.delete(gallery)
    db.session.commit()
    flash('Gallery berhasil dihapus!', 'success')
    return redirect(url_for('galeri'))

@app.route("/edit_gambar/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_gambar(id):
    image = GalleryImage.query.get_or_404(id)
    
    if request.method == 'POST':
        image.subtitle = request.form.get('subtitle')
        
        # Handle image - check both inputs
        new_image = None
        new_thumbnail = None
        has_file = 'image_file' in request.files and request.files['image_file'].filename != ''
        has_url = request.form.get('image_url_input', '').strip() != ''
        
        # Validation: only one method allowed
        if has_file and has_url:
            flash('Pilih hanya satu: Upload file ATAU masukkan URL, bukan keduanya!', 'warning')
            return redirect(url_for('edit_gambar', id=id))
        
        if has_file:
            file = request.files['image_file']
            new_image = save_image(file, folder='gallery')
            if not new_image:
                flash('Format gambar tidak valid. Gunakan PNG, JPG, atau JPEG (max 5MB)', 'warning')
                return redirect(url_for('edit_gambar', id=id))
            # Create thumbnail for uploaded file
            new_thumbnail = create_thumbnail(new_image, folder='gallery')
        elif has_url:
            new_image = request.form.get('image_url_input')
            new_thumbnail = None  # No thumbnail for URLs
        
        # Update image if new one provided
        if new_image:
            # Delete old image files if they were uploaded (not URLs)
            if image.image_url and not image.image_url.startswith('http'):
                delete_image(image.image_url)
            if image.thumbnail and not image.thumbnail.startswith('http'):
                delete_image(image.thumbnail)
            
            image.image_url = new_image
            image.thumbnail = new_thumbnail
        
        db.session.commit()
        flash('Gambar berhasil diperbarui!', 'success')
        return redirect(url_for('detail_galeri', id=image.gallery_id))
    
    return render_template("edit_gambar.html", image=image)

@app.route("/hapus_gambar/<int:id>", methods=['POST'])
@login_required
def hapus_gambar(id):
    image = GalleryImage.query.get_or_404(id)
    gallery_id = image.gallery_id
    
    # Delete image files
    if image.image_url:
        delete_image(image.image_url)
    if image.thumbnail:
        delete_image(image.thumbnail)
    
    db.session.delete(image)
    db.session.commit()
    flash('Gambar berhasil dihapus!', 'success')
    return redirect(url_for('detail_galeri', id=gallery_id))

# --- VIDEO ---

@app.route("/tambah_video", methods=['GET', 'POST'])
@login_required
def tambah_video():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        video_url = request.form.get('video_url')
        thumbnail_url = request.form.get('thumbnail_url')
        
        video_baru = Video(title=title, description=description, video_url=video_url, thumbnail_url=thumbnail_url)
        db.session.add(video_baru)
        db.session.commit()
        flash('Video berhasil ditambahkan!', 'success')
        return redirect(url_for('galeri'))
        
    return render_template("tambah_video.html")

@app.route("/video/<int:id>")
def detail_video(id):
    video = Video.query.get_or_404(id)
    return render_template("detail_video.html", video=video)

@app.route("/edit_video/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_video(id):
    video = Video.query.get_or_404(id)
    
    if request.method == 'POST':
        video.title = request.form.get('title')
        video.description = request.form.get('description')
        video.video_url = request.form.get('video_url')
        video.thumbnail_url = request.form.get('thumbnail_url')
        db.session.commit()
        flash('Video berhasil diperbarui!', 'success')
        return redirect(url_for('detail_video', id=id))
    
    return render_template("edit_video.html", video=video)

@app.route("/hapus_video/<int:id>", methods=['POST'])
@login_required
def hapus_video(id):
    video = Video.query.get_or_404(id)
    db.session.delete(video)
    db.session.commit()
    flash('Video berhasil dihapus!', 'success')
    return redirect(url_for('galeri'))

# --- AI ASSISTANT KAK YOR ---

@app.route("/chat", methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Pesan tidak boleh kosong'}), 400
        
        # System prompt untuk Kak Yor
        system_prompt = """Kamu adalah Kak Yor, asisten virtual yang ramah dan membantu untuk RST Slamet Riyadi (Rumah Sakit Tentara Tingkat III Slamet Riyadi) di Surakarta.
        
Informasi tentang RST Slamet Riyadi:
- Lokasi: Jl. Brigjend Slamet Riyadi No. 321, Surakarta
- Telepon: (0271) 714656
- Layanan: IGD 24 jam, Rawat Inap, Rawat Jalan, Laboratorium, Apotek
- Fasilitas: Ruang IGD Modern, Ruang Rawat Inap, Laboratorium lengkap

Tugasmu:
1. Menjawab pertanyaan tentang rumah sakit dengan ramah dan informatif
2. Membantu pengunjung menemukan informasi jadwal dokter, layanan, dan fasilitas
3. Memberikan arahan untuk membuat janji temu
4. Berbicara dengan sopan dan profesional
5. Jika tidak tahu jawabannya, arahkan untuk menghubungi langsung rumah sakit

Jawab dalam Bahasa Indonesia dengan ramah dan singkat (maksimal 3-4 kalimat).

JIKA USER BERTANYA TENTANG:
Dokter mata atau spesialis mata, jawab: dokter mata : DR.Wahyu Triyanto, Sp.M
Dokter gigi atau spesialis gigi, jawab: dokter gigi : DRg. Indah Lestari, Sp.KG
Dokter anak atau spesialis anak, jawab: dokter anak : DR. Siti Nurjanah, Sp.A
Dokter jantung atau spesialis jantung, jawab: dokter jantung : DR. Budi Santoso, Sp.JP
Dokter kulit atau spesialis kulit, jawab: dokter kulit : DR. Rina Marlina, Sp.KK
"""

        # Call OpenRouter API
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {app.config['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "tngtech/deepseek-r1t2-chimera:free",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            return jsonify({'response': ai_response})
        else:
            return jsonify({'error': 'Maaf, Kak Yor sedang sibuk. Silakan coba lagi.'}), 500
            
    except Exception as e:
        return jsonify({'error': 'Maaf, terjadi kesalahan. Silakan coba lagi.'}), 500

# --- AUTHENTICATION ---

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Gagal. Cek username dan password.', 'danger')
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username sudah ada.', 'warning')
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Akun berhasil dibuat! Silakan login.', 'success')
            return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- CATEGORY MANAGEMENT (Admin only) ---

@app.route("/manage_categories")
@login_required
def manage_categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template("manage_categories.html", categories=categories)

@app.route("/create_category", methods=['POST'])
@login_required
def create_category():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Nama kategori tidak boleh kosong!', 'warning')
        return redirect(url_for('manage_categories'))
    
    slug = name.lower().replace(' ', '-')
    # Check if exists
    existing = Category.query.filter_by(slug=slug).first()
    if existing:
        flash('Kategori sudah ada!', 'warning')
    else:
        new_category = Category(name=name, slug=slug)
        db.session.add(new_category)
        db.session.commit()
        flash(f'Kategori "{name}" berhasil dibuat!', 'success')
    
    return redirect(url_for('manage_categories'))

@app.route("/delete_category/<int:id>")
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    # Update all berita using this category to have no category
    Berita.query.filter_by(category_id=id).update({'category_id': None})
    db.session.delete(category)
    db.session.commit()
    flash(f'Kategori "{category.name}" berhasil dihapus!', 'success')
    return redirect(url_for('manage_categories'))

def init_db():
    with app.app_context():
        db.create_all()
        
        # Seed Data untuk Gallery (jika kosong)
        if not Gallery.query.first():
            # Gallery 1: Fasilitas Rumah Sakit
            gallery1 = Gallery(
                title="Fasilitas Rumah Sakit",
                main_image="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800"
            )
            db.session.add(gallery1)
            db.session.flush()
            
            images1 = [
                GalleryImage(subtitle="Ruang IGD Modern", image_url="https://images.unsplash.com/photo-1586773860418-d37222d8fce3?w=600", gallery_id=gallery1.id),
                GalleryImage(subtitle="Ruang Rawat Inap", image_url="https://images.unsplash.com/photo-1512678080530-7760d81faba6?w=600", gallery_id=gallery1.id),
                GalleryImage(subtitle="Laboratorium", image_url="https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=600", gallery_id=gallery1.id),
                GalleryImage(subtitle="Apotek", image_url="https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600", gallery_id=gallery1.id),
            ]
            db.session.add_all(images1)
            
            # Gallery 2: Kegiatan Sosial
            gallery2 = Gallery(
                title="Kegiatan Sosial & Bakti Kesehatan",
                main_image="https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=800"
            )
            db.session.add(gallery2)
            db.session.flush()
            
            images2 = [
                GalleryImage(subtitle="Pemeriksaan Gratis", image_url="https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=600", gallery_id=gallery2.id),
                GalleryImage(subtitle="Donor Darah", image_url="https://images.unsplash.com/photo-1615461066841-6116e61058f4?w=600", gallery_id=gallery2.id),
                GalleryImage(subtitle="Edukasi Kesehatan", image_url="https://images.unsplash.com/photo-1576765608866-5b51046452be?w=600", gallery_id=gallery2.id),
            ]
            db.session.add_all(images2)
            
            # Gallery 3: Tim Medis
            gallery3 = Gallery(
                title="Tim Medis Profesional",
                main_image="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=800"
            )
            db.session.add(gallery3)
            db.session.flush()
            
            images3 = [
                GalleryImage(subtitle="Tim Dokter Spesialis", image_url="https://images.unsplash.com/photo-1551601651-2a8555f1a136?w=600", gallery_id=gallery3.id),
                GalleryImage(subtitle="Perawat Profesional", image_url="https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=600", gallery_id=gallery3.id),
                GalleryImage(subtitle="Tenaga Medis Berpengalaman", image_url="https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=600", gallery_id=gallery3.id),
            ]
            db.session.add_all(images3)
            
            db.session.commit()
            print("✅ Gallery seed data berhasil ditambahkan!")
        
        # Seed Data untuk Video (jika kosong)
        if not Video.query.first():
            videos = [
                Video(
                    title="Profil RST Slamet Riyadi",
                    description="Video profil rumah sakit dan fasilitas yang tersedia",
                    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    thumbnail_url="https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=600"
                ),
                Video(
                    title="Protokol Kesehatan di RST Slamet Riyadi",
                    description="Panduan protokol kesehatan untuk pasien dan pengunjung",
                    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    thumbnail_url="https://images.unsplash.com/photo-1584982751601-97dcc096659c?w=600"
                ),
                Video(
                    title="Bakti Sosial Kesehatan 2026",
                    description="Dokumentasi kegiatan bakti sosial pemeriksaan kesehatan gratis",
                    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    thumbnail_url="https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=600"
                ),
            ]
            db.session.add_all(videos)
            db.session.commit()
            print("✅ Video seed data berhasil ditambahkan!")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)