import os
import requests
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rahasia-negara-aman-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rst_slamet_riyadi.db'
app.config['OPENROUTER_API_KEY'] = "-"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ================= MODELS =================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Berita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    konten = db.Column(db.Text, nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    gambar = db.Column(db.String(300), nullable=True)
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
    foto = db.Column(db.String(300), nullable=True)
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
    main_image = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relasi ke GalleryImage
    images = db.relationship('GalleryImage', backref='gallery', lazy=True, cascade='all, delete-orphan')

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subtitle = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
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

# ================= ROUTES UTAMA =================

@app.route("/")
def index():
    return render_template("index.html")

# --- BERITA & KOMENTAR ---

@app.route("/berita_acara")
def berita_acara():
    daftar_berita = Berita.query.order_by(Berita.tanggal.desc()).all()
    return render_template("berita.html", berita=daftar_berita)

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
        gambar = request.form.get('gambar') # URL Gambar
        
        berita_baru = Berita(judul=judul, konten=konten, gambar=gambar)
        db.session.add(berita_baru)
        db.session.commit()
        flash('Berita berhasil diterbitkan!', 'success')
        return redirect(url_for('berita_acara'))
        
    return render_template("tambah_berita.html")

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
        foto = request.form.get('foto')
        
        dokter_baru = Dokter(nama=nama, spesialis=spesialis, jadwal=jadwal, foto=foto)
        db.session.add(dokter_baru)
        db.session.commit()
        flash('Data Dokter berhasil ditambahkan!', 'success')
        return redirect(url_for('jadwal_dokter'))
        
    return render_template("tambah_dokter.html")

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
        flash('Permintaan janji temu berhasil dikirim! Petugas kami akan menghubungi Anda.', 'success')
        return redirect(url_for('jadwal_dokter'))
    
    # Jika GET, ambil id dokter dari query param (jika ada) untuk auto-select
    selected_dokter_id = request.args.get('dokter_id')
    daftar_dokter = Dokter.query.all()
    return render_template("buat_janji.html", dokter=daftar_dokter, selected_id=selected_dokter_id)

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
        main_image = request.form.get('main_image')
        
        gallery_baru = Gallery(title=title, main_image=main_image)
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
        image_url = request.form.get('image_url')
        
        gambar_baru = GalleryImage(subtitle=subtitle, image_url=image_url, gallery_id=gallery_id)
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
        gallery.main_image = request.form.get('main_image')
        db.session.commit()
        flash('Gallery berhasil diperbarui!', 'success')
        return redirect(url_for('detail_galeri', id=id))
    
    return render_template("edit_galeri.html", gallery=gallery)

@app.route("/hapus_galeri/<int:id>", methods=['POST'])
@login_required
def hapus_galeri(id):
    gallery = Gallery.query.get_or_404(id)
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
        image.image_url = request.form.get('image_url')
        db.session.commit()
        flash('Gambar berhasil diperbarui!', 'success')
        return redirect(url_for('detail_galeri', id=image.gallery_id))
    
    return render_template("edit_gambar.html", image=image)

@app.route("/hapus_gambar/<int:id>", methods=['POST'])
@login_required
def hapus_gambar(id):
    image = GalleryImage.query.get_or_404(id)
    gallery_id = image.gallery_id
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