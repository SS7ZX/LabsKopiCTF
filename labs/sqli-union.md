# SQLi UNION di pencarian

## Tujuan
Melihat bagaimana input pencarian yang disisipkan langsung ke query SQL dapat mengubah arti query. Dalam latihan lokal ini, gabungkan hasil pencarian produk dengan satu baris dari tabel latihan `secrets`, lalu bandingkan perilakunya dengan mode Secure.

## Konsep
Pencarian rentan memakai query dengan bentuk `SELECT id,name,price,description FROM products WHERE name LIKE '%INPUT%' AND id<99`. Teks `INPUT` seharusnya hanya menjadi kata yang dicari. Karena aplikasi menyisipkan teks itu langsung ke dalam SQL, tanda kutip dalam input dapat menutup teks pencarian dan mengubah struktur query.

`UNION` menggabungkan hasil dari dua perintah `SELECT`. Agar dapat digabungkan, kedua hasil harus memiliki jumlah kolom yang sama dan urutan kolom yang sesuai. Query produk di lab ini menghasilkan empat kolom: `id`, `name`, `price`, dan `description`. Tabel latihan `secrets` mempunyai kolom `name` dan `value`; data flag disimpan pada kolom `value`.

Semua percobaan dalam materi ini hanya berlaku untuk database lokal KopiLab. Jangan gunakan contoh atau teknik ini pada situs, jaringan, atau database lain.

## Hint 1
Mulai dengan pencarian biasa seperti `Gayo`. Di halaman hasil, perhatikan Request Inspector dan cari query pencarian. Teks pencarian biasa muncul di dalam pola `LIKE '%...%'`.

## Hint 2
Perhatikan query sumber: hasilnya memiliki empat kolom. `UNION SELECT` juga harus menghasilkan empat nilai. Pada contoh lab, nilai pertama dan ketiga adalah angka, nilai kedua adalah teks `flag`, dan nilai keempat mengambil `value` dari tabel latihan.

## Hint 3
Pada input uji, tanda kutip pertama menutup teks pencarian, `UNION SELECT` menambahkan satu baris dari `secrets`, dan `-- ` membuat sisa query yang ditambahkan aplikasi menjadi komentar SQL. Pastikan ada spasi setelah dua tanda minus.

## Solusi
Dalam mode Vulnerable, kirim input uji lokal berikut melalui pencarian KopiLab: `%' UNION SELECT 1,'flag',1,value FROM secrets-- `. Baris hasil gabungan memakai kolom keempat untuk menampilkan nilai flag pada deskripsi produk. Salin flag yang tampil ke form submit flag pada halaman lab ini.

## Akar masalah
Fungsi pencarian membuat query dengan menyisipkan input langsung ke string SQL. Akibatnya, database tidak dapat membedakan teks pencarian yang dimasukkan pengguna dari bagian sintaks query.

## Perbaikan
Gunakan query berparameter seperti `SELECT id,name,price,description FROM products WHERE name LIKE ? AND id<99`, lalu kirim pola pencarian sebagai nilai parameter, misalnya `("%" + query + "%",)`. Database memperlakukan nilai itu sebagai data pencarian, bukan sebagai sintaks SQL. Dalam mode Secure, input UNION yang sama dicari sebagai teks dan tidak menambahkan hasil dari tabel `secrets`.

## Contoh rentan
`SELECT id,name,price,description FROM products WHERE name LIKE '%` + query + `%' AND id<99`

## Contoh aman
`connection.execute("SELECT id,name,price,description FROM products WHERE name LIKE ? AND id<99", ("%" + query + "%",))`

## Langkah latihan
- Pastikan aplikasi KopiLab berjalan di komputermu sendiri pada `http://127.0.0.1:5000`. Pada halaman lab ini, pilih mode `Vulnerable` dari tombol mode di bagian atas. Mode ini memang disediakan untuk latihan lokal.
- Buka Burp Suite, pilih `Proxy`, lalu klik `Open browser`. Di browser Burp, buka KopiLab dan gunakan kotak pencarian untuk mencari `Gayo`. Jangan nyalakan Intercept dulu; pastikan statusnya `Intercept is off` supaya browser tidak tertahan.
- Kembali ke Burp dan buka `Proxy > HTTP history`. Pilih request terbaru ke host `127.0.0.1`, port `5000`, dengan path `/search`. Request pencarian biasanya memakai method `GET`; nilai pencarian dikirim sebagai parameter `q`.
- Buka detail request dan temukan parameter `q=Gayo`. Ini adalah contoh request normal. Di halaman hasil KopiLab, buka Request Inspector dan lihat query yang dicatat. Query normal berbentuk `SELECT id,name,price,description FROM products WHERE name LIKE '%Gayo%' AND id<99`.
- Kembali ke halaman KopiLab. Ganti kata `Gayo` pada kotak pencarian dengan input uji berikut, persis termasuk spasi di akhir: `%' UNION SELECT 1,'flag',1,value FROM secrets-- `. Tekan tombol Cari. Menggunakan form membantu browser mengodekan karakter khusus di URL dengan benar.
- Kembali ke `Proxy > HTTP history` dan pilih request `/search` yang baru saja dibuat. Pada parameter `q`, Burp mungkin menampilkan karakter khusus dalam bentuk URL-encoded. Itu normal: encoding hanya cara browser menuliskan karakter di URL. Lihat parameter yang sudah di-decode jika tersedia, lalu pastikan request menuju `127.0.0.1:5000`, bukan host lain.
- Perhatikan hasil pencarian di browser. Dalam mode Vulnerable, satu baris tambahan dari tabel `secrets` dapat muncul dan nilai flag ditampilkan sebagai deskripsi hasil. Salin nilai flag yang tampil, kembali ke form submit di halaman lab, lalu kirim flag tersebut untuk mencatat progres.
- Untuk memahami mengapa input tadi bekerja, bayangkan aplikasi menempelkan input ke pola `LIKE '%INPUT%'`. Query yang terbentuk secara garis besar menjadi `SELECT id,name,price,description FROM products WHERE name LIKE '%%' UNION SELECT 1,'flag',1,value FROM secrets-- %' AND id<99`. Bagian `UNION SELECT` menambahkan hasil kedua. Empat nilai yang dipilih cocok dengan empat kolom hasil produk. `-- ` mengomentari sisa teks query yang ditambahkan aplikasi.
- Ganti mode KopiLab menjadi `Secure`, lalu kirim input uji yang sama melalui kotak pencarian. Kali ini input diperlakukan sebagai nilai pencarian biasa. Baris dari `secrets` tidak boleh muncul. Bandingkan hasil ini dengan mode Vulnerable dan perhatikan bahwa perbaikannya dilakukan pada query server, bukan dengan mengandalkan browser untuk menyaring input.
- Jika Burp menampilkan terlalu banyak entri, pilih request terbaru dengan host `127.0.0.1` dan port `5000`. Jika browser berhenti memuat, periksa `Proxy > Intercept`; teruskan request yang tertahan dengan `Forward`, lalu matikan Intercept. Jangan mengirim request ke tujuan selain KopiLab lokal.

## Kalau masih bingung
Anggap query SQL sebagai kalimat yang disusun server. Pada mode rentan, aplikasi menempelkan kata pencarianmu langsung ke kalimat itu. Input uji memakai tanda kutip untuk keluar dari bagian teks, `UNION SELECT` untuk menambahkan hasil empat kolom, dan `-- ` untuk mengabaikan sisa kalimat. Pada mode Secure, query memakai tanda tanya sebagai tempat parameter. Database menerima input sebagai data biasa sehingga kata-kata SQL di dalamnya tidak dijalankan sebagai perintah.
