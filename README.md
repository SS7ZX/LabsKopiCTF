# KopiLab

KopiLab adalah toko kopi simulasi dan platform belajar keamanan aplikasi web.
Mode Vulnerable sengaja memiliki bug untuk latihan; gunakan hanya di komputer
sendiri. Aplikasi dan simulator hanya bind ke `127.0.0.1`. Jangan expose port
KopiLab ke LAN atau internet.

## Jalankan di Windows

Persyaratan: Python 3.10 atau lebih baru. Instal dependensi satu kali:

```bat
cd C:\kopilab
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python run.py
```

Kemudian buka <http://127.0.0.1:5000>. Aplikasi tidak memerlukan internet saat
runtime; CSS, JavaScript, dan ilustrasi SVG disimpan di `kopilab/static`.

Akun latihan seed:

| Username | Password | Kegunaan |
|---|---|---|
| `budi` | `budi123` | Akun pelanggan |
| `siti` | `siti123` | Akun pelanggan kedua |
| `admin` | `Adm1n!Sup3r#x` | Target latihan admin |

Database `kopilab.db` dibuat otomatis saat aplikasi pertama kali berjalan.
Untuk mereset lewat command line, hentikan server lalu jalankan
`python run.py --reset`. Halaman `/labs` juga menyediakan tombol reset progres
sendiri dan reset seluruh database latihan.

### Browser simulator (opsional)

Beberapa latihan memakai halaman simulator lokal pada port 9000. Jalankan di
terminal kedua:

```bat
cd C:\kopilab
.venv\Scripts\activate
python run_attacker.py
```

Buka <http://127.0.0.1:9000>. Simulator hanya menyediakan form demonstrasi
untuk aplikasi KopiLab lokal; ia tidak memindai host, menebak password,
membaca cookie, atau mengirim data ke layanan lain. Hentikan dengan `Ctrl+C`.

## Mulai belajar

1. Pastikan banner aplikasi sengaja rentan terlihat dan mulai dalam **Vulnerable**.
2. Pilih lab dari katalog; baca tujuan, konsep, dan endpoint target.
3. Ikuti langkah praktikum lokal. Kalau bingung, buka tiga petunjuk satu per satu.
4. Submit flag untuk mencatat progres di SQLite.
5. Jika masih stuck, tombol **Buka solusi lengkap** tersedia kapan saja—tidak perlu
   membuka semua petunjuk terlebih dahulu.
6. Ganti ke **Secure** dan ulangi permintaan untuk membandingkan hasilnya.
7. Lihat scoreboard SQLite atau unduh template laporan Markdown per lab.

Untuk penjelasan arsitektur, database, alur request, seluruh route utama,
mode, Inspector, dan peta 20 lab, buka menu **Deep Dive** di navigasi atau
kunjungi <http://127.0.0.1:5000/guide>.

Setiap halaman lab menggunakan bahasa sederhana dan menyediakan tujuan,
alamat tempat mencoba, langkah praktikum, tiga petunjuk bertahap, solusi,
alasan bug terjadi, dan cara memperbaikinya. Membuka solusi bukan kegagalan:
baca penjelasannya, lalu coba ulang sendiri di mode Secure.

### Istilah keamanan dengan bahasa sederhana

| Istilah | Artinya |
|---|---|
| SQL injection | Teks pencarian/login keliru dibaca database sebagai bagian perintah. |
| XSS | Tulisan dari pengunjung keliru dibaca browser sebagai HTML atau skrip. |
| IDOR | Server menunjukkan data hanya karena seseorang menebak nomor data itu. |
| CSRF | Browser mengirim aksi dengan akunmu tanpa memastikan kamu memang bermaksud melakukannya. |
| Path traversal | Nama file membuat server keluar dari folder yang seharusnya boleh dibuka. |
| SSRF | Server diminta membuka alamat; KopiLab membatasi contoh ini ke service lokalnya sendiri. |
| Secure mode | Versi latihan yang menambahkan pemeriksaan untuk menolak perilaku rentan. |

Mode tersimpan per browser. Secure mode menggunakan handler yang sama dengan
validasi/query aman, bukan server terpisah. Data progres disimpan di SQLite;
cookie hanya membawa pengenal acak pelajar dan sesi.

## Peta fitur dan kode

```text
run.py                    entry point loopback, debug nonaktif
run_attacker.py           entry point simulator lokal opsional (127.0.0.1:9000)
kopilab/__init__.py        app factory, mode, konteks template, inspector
kopilab/db.py              schema, migrasi ringan, dan seed SQLite
kopilab/config.py          konfigurasi, daftar lab, dan flag kompatibilitas
kopilab/blueprints/        route toko, auth, akun, admin, API, file, dan lab
kopilab/vulns/             implementasi vuln/fix yang diisolasi per lab
kopilab/templates/         halaman Jinja yang mewarisi base.html
kopilab/static/            CSS, JavaScript, dan ilustrasi SVG lokal
labs/                      materi Markdown per ID lab
attacker/                  halaman simulator browser statis dan loopback-only
tests/                      uji exploit lokal, mode aman, dan fitur toko
```

Toko menyediakan katalog 15+ produk, halaman detail, keranjang multi-item,
checkout, riwayat pesanan, akun, wishlist, dan ulasan rating. Route toko lama
untuk latihan (mis. `/search`, `/checkout`, `/order/<id>`) tetap tersedia.
Banner peringatan ditampilkan konsisten pada halaman HTML. Request Inspector
opsional mencatat request terakhir, SQL yang dicatat handler, dan header respons
ke database lokal.

## Lab yang tersedia

Semua lab lama dan flag dipertahankan. OWASP di bawah memakai Top 10 2021.

| ID | Topik | OWASP | Level |
|---|---|---|---|
| `sqli-union` | SQL injection UNION pada pencarian | A03 | Easy |
| `sqli-login` | SQL injection autentikasi | A03 | Easy |
| `xss` | Reflected dan stored XSS | A03 | Easy |
| `idor-order` | IDOR detail pesanan | A01 | Easy |
| `idor-api` | IDOR API pengguna | A01 | Easy |
| `logic-price` | Harga checkout dari klien | A04 | Easy |
| `logic-balance` | Kuantitas negatif dan kupon | A04 | Medium |
| `mass-assign` | Mass assignment profil | A04 | Medium |
| `bac-cookie` | Otorisasi berdasarkan cookie | A01 | Easy |
| `csrf` | CSRF transfer | A01 | Medium |
| `traversal` | Path traversal (hanya file dalam proyek) | A01 | Easy |
| `ssrf` | SSRF ke service simulasi loopback | A10 | Medium |
| `reset` | Token reset yang dapat ditebak | A07 | Medium |
| `blind-sqli` | Boolean SQLi oracle lokal | A03 | Medium |
| `upload` | Validasi upload lemah, file tidak dieksekusi | A04 | Easy |
| `jwt` | JWT dengan secret demo lemah | A07 | Medium |
| `race-coupon` | Race/check-then-act kupon | A04 | Hard |
| `open-redirect` | Redirect ke simulator loopback | A01 | Easy |
| `rate-limit` | Batas percobaan login lemah | A07 | Medium |
| `filter-bypass` | Filter case-sensitive | A03 | Hard |

Lab baru memiliki materi, tiga hint, solusi, akar masalah, perbaikan, metadata,
dan flag sendiri. Endpoint tambahan ada di `/extra/` dan tetap dibatasi pada
data maupun tujuan latihan lokal.

## Menambah lab

1. Tambahkan fungsi dengan type hints dan docstring di `kopilab/vulns/<nama>.py`.
   Beri komentar `# VULN[<lab-id>]` tepat pada perilaku yang sengaja rentan.
2. Implementasikan perilaku Secure pada fungsi yang sama melalui argumen
   `secure` atau parameter konteks; endpoint tetap berada di blueprint lokal.
3. Tambahkan flag, judul, kategori, level, endpoint, dan metadata di
   `kopilab/config.py`.
4. Tulis materi `labs/<lab-id>.md` dengan bagian Tujuan, Konsep, Hint 1–3,
   Solusi, Akar masalah, Perbaikan, Contoh rentan, dan Contoh aman.
5. Tambahkan tes eksploit terbatas ke `tests/test_exploits.py` atau
   `tests/test_additional_labs.py`, serta tes penolakan di
   `tests/test_secure_mode.py`.
6. Jalankan `python -m pytest -q` sebelum menerima perubahan.

Pertahankan batas lokal: tidak ada URL/host eksternal sebagai target, eksekusi
upload, atau akses file di luar folder proyek.

## Tes

Dengan virtual environment aktif:

```bat
python -m pytest -q
```

Tes menggunakan database sementara dan service simulasi loopback; tes tidak
menyentuh database seed pribadi di `kopilab.db`.
# LabsKopiCTF
