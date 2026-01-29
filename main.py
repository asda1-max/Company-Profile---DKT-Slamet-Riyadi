import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rahasia-negara-aman-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rst_slamet_riyadi.db'
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
        # Seed Data jika kosong (Optional)
        if not Berita.query.first():
            # ... (Seed code sama seperti sebelumnya) ...
            pass

if __name__ == "__main__":
    init_db()
    app.run(debug=True)