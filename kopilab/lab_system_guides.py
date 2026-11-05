"""Per-lab explanations of request flow, learning goals, and stored state."""

LAB_SYSTEM_GUIDES = {
    "sqli-union": {
        "objectives": [
            "Membedakan input pencarian sebagai data biasa dari input yang ikut mengubah struktur query SQL.",
            "Membuktikan dampak dari baris hasil yang benar-benar berubah, bukan hanya dari status HTTP atau error.",
        ],
        "flow": "Browser mengirim GET /search?q=... -> route search membaca query string -> helper search_query memilih query rentan atau parameterized -> SQLite membaca products (dan pada latihan rentan dapat menggabungkan secrets) -> template merender hasil.",
        "state": "Membaca tabel products dan secrets; tidak mengubah database. Request Inspector menyimpan jejak query untuk pelajar. Secure memakai placeholder SQL dan parameter nilai q.",
        "reasoning": "Baseline menunjukkan bentuk dan jumlah hasil normal. Perubahan q saja mengisolasi apakah input mengubah query. Cocokkan baris/kolom hasil dan query Inspector; pesan sukses atau error SQL saja belum membuktikan data tambahan.",
    },
    "sqli-login": {
        "objectives": [
            "Memahami perbedaan autentikasi berbasis query rentan dan pencocokan kredensial berparameter.",
            "Mengikuti dampak dari query ke pembentukan session uid/user dan redirect sesudah login.",
        ],
        "flow": "POST /login menerima username/password -> login_query menyusun query menurut mode -> SQLite mencari baris users -> jika ada baris, route menulis uid/user ke session dan mengirim redirect /me; jika tidak, form login dirender lagi.",
        "state": "Sumber identitas adalah tabel users. Login sukses mengubah session browser dan cookie admin yang menyertai respons; percobaan gagal tidak seharusnya membuat identitas baru. Secure memakai parameter query.",
        "reasoning": "Jangan berhenti pada 302. Buka /me untuk memastikan siapa yang benar-benar menjadi principal. Bandingkan input, query Inspector, session yang terbentuk, dan akun hasil; jangan menyalin cookie sesi.",
    },
    "xss": {
        "objectives": [
            "Membedakan reflected output pada hasil pencarian dari stored content yang tersimpan lalu dirender lagi.",
            "Menentukan konteks HTML yang digunakan saat output ditulis dan bagaimana escaping mengubah perlakuan browser.",
        ],
        "flow": "Reflected: GET /search?q=... -> route memasukkan q ke template. Stored: POST /review menyimpan body/author/rating -> redirect /product/<id> -> route membaca reviews lalu merendernya di halaman produk.",
        "state": "Stored review menetap di tabel reviews SQLite sampai data latihan direset; reflected query tidak disimpan. Secure meng-escape output saat render. Jangan gunakan tes yang membaca atau mengirim cookie.",
        "reasoning": "Bandingkan request, raw response HTML, dan tampilan browser. Untuk stored case, bukti utamanya adalah teks yang muncul kembali pada GET produk setelah POST. Pisahkan eksperimen refleksi dan penyimpanan supaya sumber output jelas.",
    },
    "idor-order": {
        "objectives": [
            "Memahami bahwa autentikasi membuktikan siapa pengguna, tetapi tidak otomatis memberi akses ke semua order.",
            "Mengamati kontrol kepemilikan objek pada lookup order.",
        ],
        "flow": "Browser meminta GET /order/<id> -> route memastikan login -> helper get_order mencari orders berdasarkan id; Secure menambahkan batas user_id dari session -> template menampilkan order.",
        "state": "Tabel orders berisi user_id pemilik, item, qty, total, dan note. GET hanya membaca data. Seed lokal menyediakan order milik Budi dan record akun lain untuk pembanding.",
        "reasoning": "Pertahankan sesi Budi dan ubah hanya ID path dari order miliknya ke ID fixture yang disebut materi. Respons 200 baru menjadi temuan jika body benar-benar menunjukkan order asing; Secure harus menghilangkan record itu dari hasil.",
    },
    "idor-api": {
        "objectives": [
            "Membedakan izin mengakses endpoint API dari izin membaca record user tertentu.",
            "Mengidentifikasi field sensitif yang ikut keluar saat objek user diambil.",
        ],
        "flow": "GET /api/user/<uid> -> require_login menetapkan principal sesi -> helper get_user mengambil users berdasarkan uid -> JSON mengembalikan field profil; Secure juga membatasi query pada uid sesi.",
        "state": "Sumbernya tabel users; request GET tidak mengubahnya. Nilai api_key admin pada respons adalah fixture dari konfigurasi flag, bukan kolom api_key di database.",
        "reasoning": "Gunakan /api/user/2 sebagai baseline Budi, lalu ubah hanya ID ke fixture admin /api/user/1. Bandingkan JSON id/username/role/balance dan jangan salin nilai sensitif. Secure harus tetap mengizinkan objek sendiri.",
    },
    "logic-price": {
        "objectives": [
            "Menemukan perbedaan antara harga produk tepercaya di katalog dan harga yang dikirim browser.",
            "Mengikuti efek bisnis sampai order dibuat dan saldo user diperbarui.",
        ],
        "flow": "POST /checkout -> require_login -> route membaca produk berdasarkan pid -> Vulnerable memakai request.form price, Secure memakai products.price -> hitung total -> INSERT orders -> UPDATE users.balance -> commit dan render bukti order.",
        "state": "Menulis tabel orders dan mengurangi balance pada users; ini bukan tes read-only. Produk 99 adalah fixture harga ekstrem. Periksa saldo sebelum mencoba dan reset data lokal bila perlu.",
        "reasoning": "Baseline checkout normal memperlihatkan pid/price/qty. Ubah price saja satu kali lalu periksa total order dan saldo—status 200 tidak cukup. Pada Secure, harga harus mengikuti products.price meskipun request membawa nilai lain.",
    },
    "logic-balance": {
        "objectives": [
            "Memahami invariant kuantitas positif dan larangan memakai kupon berulang.",
            "Memisahkan pengaruh qty negatif dari pengaruh coupon stacking.",
        ],
        "flow": "POST /checkout mengumpulkan qty dan semua nilai coupon -> Secure memvalidasi qty, daftar kupon, dan keunikan -> helper calculate_total menghitung harga x qty - diskon -> route menulis order, memperbarui balance, lalu commit.",
        "state": "Menulis orders dan users.balance. Kupon HEMAT50 bernilai Rp50.000 di fixture; kupon yang dikirim berulang mengurangi total berulang kali pada jalur rentan.",
        "reasoning": "Catat saldo awal. Uji satu kondisi per order: pertama qty, pada percobaan terpisah kupon duplikat. Bandingkan body yang dikirim, total tersimpan, dan saldo. Secure harus menolak nilai invalid sebelum ada perubahan database.",
    },
    "mass-assign": {
        "objectives": [
            "Memahami bahwa field pada request dapat dimanipulasi terlepas dari kontrol form UI.",
            "Menguji allowlist atribut profil dan perubahan role persisten.",
        ],
        "flow": "POST /profile -> require_login mengambil uid dari session -> update_profile mengiterasi semua field form -> Vulnerable membangun UPDATE users dari nama field, Secure menerima email saja -> commit -> redirect /me.",
        "state": "Menulis baris users milik principal aktif. Field role adalah atribut hak akses; jika berubah, efek tetap ada setelah redirect sampai database direset atau role dikembalikan.",
        "reasoning": "Baseline body berisi email saja. Tambahkan hanya role=admin, lalu ikuti redirect ke /me dan cek role aktual serta flag. Keberhasilan redirect bukan bukti mass assignment; role di database adalah bukti.",
    },
    "bac-cookie": {
        "objectives": [
            "Membedakan cookie yang dikontrol klien dari principal/role yang dipercaya server.",
            "Membandingkan pemeriksaan otorisasi Vulnerable dan Secure.",
        ],
        "flow": "GET /admin -> route membaca cookie admin -> Vulnerable mempercayai nilai cookie; Secure mengambil role dari tabel users untuk uid dalam session -> akses ditolak atau daftar users dirender.",
        "state": "GET tidak mengubah database. admin=1 adalah cookie latihan terpisah dari Flask session; Secure authorization memakai users.role. Jangan menyalin cookie sesi atau token.",
        "reasoning": "Login sebagai Budi, simpan respons 403 baseline, lalu ubah hanya cookie admin di Repeater sesuai materi. Bukti adalah panel admin yang keluar, bukan sekadar perubahan status. Secure harus menolak karena role DB Budi tetap user.",
    },
    "csrf": {
        "objectives": [
            "Memahami bahwa browser membawa kredensial sesi secara otomatis dan server perlu bukti niat untuk aksi sensitif.",
            "Mengamati token anti-CSRF dan efek transfer pada kedua akun latihan.",
        ],
        "flow": "Form demo lokal di port 9000 memicu POST /transfer ke KopiLab -> require_login mengambil sender dari session -> Secure membandingkan csrf_token form dengan token sesi -> helper mengurangi balance pengirim dan menambah balance penerima.",
        "state": "Menulis users.balance untuk pengirim dan penerima. GET /me membentuk csrf_token di session; Secure menolak token salah sebelum helper/database dipanggil. Gunakan simulator lokal saja.",
        "reasoning": "Catat saldo dua akun, method/body, Referer dan keberadaan token (tanpa nilainya). Bandingkan request demo rentan dengan Secure; periksa saldo sesudahnya. Jangan mengulang transfer karena setiap POST dapat memindahkan saldo fixture.",
    },
    "traversal": {
        "objectives": [
            "Memahami bagaimana normalisasi path dan batas direktori menentukan file yang boleh dibaca.",
            "Membedakan fixture file proyek dari file sistem operasi yang tidak termasuk latihan.",
        ],
        "flow": "GET /download?file=... -> resolve_training_file menggabungkan nama dengan folder files lalu resolve path -> Vulnerable mengizinkan root project, Secure membatasi root files -> route membaca teks dan mengirim response.",
        "state": "Tidak memakai SQLite dan tidak mengubah file. Fixture aman ada di files/welcome.txt; secret.txt adalah marker latihan di root proyek. Akses di luar project tetap dibatasi simulator.",
        "reasoning": "Mulai dari welcome.txt sebagai kontrol. Ubah hanya parameter file ke path fixture project yang disebut materi; periksa body teks dan status. Secure tetap melayani welcome.txt tetapi menolak path di luar direktori files.",
    },
    "ssrf": {
        "objectives": [
            "Memahami perbedaan koneksi browser ke endpoint preview dan koneksi server ke target URL.",
            "Menganalisis allowlist tujuan berdasarkan scheme, hostname, port, dan path.",
        ],
        "flow": "Browser mengirim GET /preview?url=... -> route memanggil fetch_internal_url dari server KopiLab -> helper memvalidasi URL dan menghubungi service latihan 127.0.0.1:5001 -> hasil service dimasukkan ke halaman preview.",
        "state": "Tidak membaca database atau mengubah data. Tujuan latihan hanya service internal loopback port 5001; helper menonaktifkan proxy lingkungan. Jangan mengubah URL ke host atau jaringan lain.",
        "reasoning": "Catat URL input, error/hasil yang dikembalikan server, dan port/path. Browser hanya berbicara ke port 5000; fetch ke port 5001 dilakukan server. Secure mempertahankan target service latihan yang tepat dan menolak variasi lain.",
    },
    "reset": {
        "objectives": [
            "Memahami lifecycle reset password: meminta token, mengikat token ke akun, memvalidasi, lalu mengubah kredensial.",
            "Membandingkan token prediktif Vulnerable dengan hash token acak, expiry, dan penggunaan sekali pada Secure.",
        ],
        "flow": "POST /reset step=request menerima username -> Vulnerable menghitung MD5 username sebagai token; Secure membuat token acak dan menyimpan hash/expiry -> POST langkah berikutnya memvalidasi -> reset_password memperbarui users.password.",
        "state": "Mengubah users.password. Secure juga menulis password_reset_tokens dengan token_hash dan expires_at lalu menghapus baris setelah sukses. Gunakan akun seed dan password latihan, jangan mengubah akun pribadi.",
        "reasoning": "Ikuti dua request form: request token lalu submit token/password. Periksa username, step, status/pesan, dan perubahan login pada akun seed. Jangan memasukkan token aktif ke catatan; hindari mengulang perubahan password tanpa perlu.",
    },
    "blind-sqli": {
        "objectives": [
            "Memahami oracle boolean: respons hanya membocorkan benar/salah, bukan hasil query lengkap.",
            "Membedakan input yang diteruskan ke evaluasi SQL dari kontrol aman di Secure.",
        ],
        "flow": "GET /extra/blind-sqli?condition=... -> evaluate_condition menjalankan kondisi terbatas terhadap koneksi SQLite -> route hanya mengembalikan result/error boolean -> flag latihan muncul hanya pada kondisi true Vulnerable.",
        "state": "Membaca SQLite dan tidak memodifikasi tabel. Endpoint sengaja membatasi output ke boolean; jangan memperluas latihan menjadi ekstraksi data. Secure menolak pola kondisi mentah sesuai helper.",
        "reasoning": "Bandingkan satu kondisi false dan satu kondisi true yang memang disediakan materi. Catat result, error, status, dan flag. Perbedaan satu bit adalah sinyal, bukan konten data; jangan membuat rangkaian enumerasi.",
    },
    "upload": {
        "objectives": [
            "Menganalisis validasi upload pada nama/ekstensi dan batas penyimpanan.",
            "Memahami bahwa nama file, MIME, lokasi simpan, dan eksekusi adalah kontrol berbeda.",
        ],
        "flow": "POST /extra/upload menerima multipart file -> route mengecek field/nama -> helper upload_allowed memeriksa ekstensi menurut mode -> target diselesaikan di folder uploads proyek -> file disimpan dan JSON dikembalikan.",
        "state": "Menulis file di folder uploads proyek, bukan SQLite. File latihan tidak pernah dieksekusi. Gunakan file teks kecil bernama unik dan hapus hanya file latihan yang kamu buat bila diperlukan.",
        "reasoning": "Tangkap multipart dari form, pertahankan boundary, lalu analisis filename, Content-Type, status, saved, dan flag. Secure harus menolak file teks tetapi tidak mengubah folder tujuan. Jangan mengunggah file executable atau data pribadi.",
    },
    "jwt": {
        "objectives": [
            "Membedakan payload yang sekadar Base64 dari signature yang mengautentikasi token.",
            "Memahami dampak pemilihan secret verifikasi pada penerimaan klaim role.",
        ],
        "flow": "GET /extra/jwt membuat token fixture -> POST /extra/jwt menerima token -> decode_token memeriksa struktur, alg HS256, dan HMAC -> route mengembalikan claims yang valid; role admin memicu flag hanya pada mode rentan.",
        "state": "Tidak memakai database; token dan kunci berasal dari konfigurasi/helper. Secure memakai secret berbeda yang tidak dapat dilihat dari UI. Jangan gunakan token, secret, atau akun dari layanan nyata.",
        "reasoning": "Simpan token fixture secara lokal hanya selama tes. Bandingkan token apa adanya, penolakan token yang tidak valid, claims response, dan flag. Mengedit payload saja tidak cukup jika signature tidak cocok; Secure menolak token lama.",
    },
    "race-coupon": {
        "objectives": [
            "Memahami pola check-then-act dan pentingnya constraint/transaksi atomik untuk aksi one-time.",
            "Membedakan demo duplikasi state dari uji konkurensi/flood.",
        ],
        "flow": "POST /extra/coupon -> route membaca user_id session -> redeem_coupon menghitung redemption lalu insert coupon_redemptions -> commit -> response menyatakan jumlah redemption.",
        "state": "Persisten di tabel coupon_redemptions berdasarkan user_id dan coupon. Secure mengambil transaksi BEGIN IMMEDIATE, memeriksa lalu menulis secara atomik; reset database latihan dapat membersihkan state.",
        "reasoning": "Login sebagai Budi dan kirim satu baseline, lalu satu pengulangan manual sesuai lab. Amati counter dan flag. Ini simulasi check-then-insert, bukan benchmark race; jangan gunakan parallel requests, loop, atau Intruder.",
    },
    "open-redirect": {
        "objectives": [
            "Membedakan redirect relatif internal dari tujuan absolut yang tidak disetujui.",
            "Membaca status 302 dan header Location sebagai bagian dari hasil, bukan menganggap redirect sebagai akses server.",
        ],
        "flow": "GET /extra/redirect?next=... -> allowed_redirect menilai tujuan -> route mengirim 302 Location atau 400 -> flag hanya untuk tujuan simulator lokal pada Vulnerable.",
        "state": "Tidak membaca/menulis SQLite dan tidak mengubah session bisnis. Pengalihan absolut yang disimulasikan hanya ke 127.0.0.1:9000; tidak ada tujuan internet.",
        "reasoning": "Baseline /labs memastikan redirect relatif tetap bekerja. Ubah hanya next ke simulator lokal, kemudian periksa status dan Location di Repeater. Secure menolak tujuan absolut tersebut tetapi mempertahankan path internal.",
    },
    "rate-limit": {
        "objectives": [
            "Memahami rate limit sebagai state kumulatif per identitas, bukan satu request yang berdiri sendiri.",
            "Mengamati batas dan respons throttling tanpa melakukan password guessing.",
        ],
        "flow": "POST /extra/rate-login -> route mengambil player_id anonim dari session -> record_login_attempt membaca/menambah login_attempts di SQLite -> Secure memberi 429 setelah ambang, Vulnerable menandai counter latihan.",
        "state": "Tabel login_attempts memiliki player_id, attempts, last_attempt; ini penghitung lab dan bukan autentikasi password. State dapat bertahan sampai reset database/identitas pemain baru.",
        "reasoning": "Catat counter awal lalu kirim hanya jumlah request manual yang disebut materi (maksimum enam). Bandingkan attempts/status setiap respons. Jangan memakai Intruder, automasi, atau kredensial.",
    },
    "filter-bypass": {
        "objectives": [
            "Memahami mengapa aturan blokir harus melakukan normalisasi konsisten sebelum membandingkan input.",
            "Menguji satu variasi kapitalisasi dan melihat keputusan filter boolean.",
        ],
        "flow": "GET /extra/filter?q=... -> blocked_username membandingkan reserved name menurut mode -> route mengembalikan JSON blocked dan mungkin flag; tidak ada akun yang dibuat.",
        "state": "Tidak mengubah database atau membuat pengguna. Hasil hanya boolean dari helper. Secure menormalisasi input agar perbedaan kapitalisasi tidak melewati pemeriksaan.",
        "reasoning": "Kirim admin sebagai baseline, lalu ubah hanya kapitalisasi menjadi ADMIN. Bandingkan blocked/status/flag; jika dua input berbeda hasilnya, jelaskan urutan normalisasi dan pemeriksaan.",
    },
    "burp-repeater": {
        "objectives": [
            "Menggunakan Repeater untuk menambahkan field yang tidak ditawarkan UI dan mengevaluasi allowlist server.",
            "Menghubungkan perubahan request role dengan baris users dan otorisasi sesi sesudahnya.",
        ],
        "flow": "POST /extra/burp-profile -> require_login mengambil uid -> route menerima email/role dan menolak nama/role yang tidak dikenal -> update_profile menulis users -> JSON role aktual dikembalikan.",
        "state": "Mengubah email/role pada baris users milik Budi. Mode Secure hanya membiarkan email; role aktual dibaca ulang dari database sebelum response/flag.",
        "reasoning": "Bandingkan form email baseline dengan body yang ditambah role=admin. Periksa JSON role dan X-Lab-Flag, lalu buka /me untuk verifikasi persisten. Jangan mengubah cookie/session; eksperimen ini tentang field body.",
    },
    "cors-policy": {
        "objectives": [
            "Memahami bahwa CORS adalah kebijakan browser yang dinyatakan melalui response header, bukan autentikasi API.",
            "Menganalisis hubungan Origin, allow-origin, credentials, dan mode.",
        ],
        "flow": "GET /extra/academy/cors-policy membaca Origin dari query/header -> evaluator membandingkan allowlist fixture -> response JSON dan Access-Control-Allow-* dikirim ke browser.",
        "state": "Tidak memakai database atau mengubah sesi bisnis. Kebijakan berasal dari konstanta allow-origin lokal; request ke training.invalid hanya nilai header, bukan koneksi ke host itu.",
        "reasoning": "Bandingkan tanpa Origin, Origin lokal yang tepat, dan marker training.invalid. Baca ACAO/credentials serta policy; jangan simpulkan data bisa dicuri dari header saja atau melakukan request ke origin luar.",
    },
    "clickjacking-headers": {
        "objectives": [
            "Memahami bagaimana CSP frame-ancestors dan X-Frame-Options membatasi framing halaman.",
            "Membedakan header anti-framing dari pemeriksaan autentikasi/otorisasi.",
        ],
        "flow": "GET endpoint demo -> evaluator memilih header menurut mode -> JSON menjelaskan frameable dan response header menunjukkan kebijakan browser.",
        "state": "Tidak ada database atau perubahan session. Fixture hanya menyajikan dashboard latihan; tidak membuat iframe atau memuat halaman luar.",
        "reasoning": "Bandingkan header Vulnerable yang absen dengan Secure yang memberi frame-ancestors 'none' dan DENY. Body JSON tetap serupa; bukti perbaikan ada pada response header.",
    },
    "security-headers": {
        "objectives": [
            "Mengenali peran header CSP, nosniff, Referrer-Policy, dan Permissions-Policy.",
            "Memahami header sebagai defense-in-depth, bukan pengganti validasi, encoding, atau kontrol akses.",
        ],
        "flow": "GET endpoint statis -> evaluator membentuk JSON tetap -> Secure menambahkan kebijakan response headers -> browser menerima kebijakan.",
        "state": "Tidak menyentuh database atau sesi. Body fixture tetap statis agar perbandingan isolasi header-nya jelas.",
        "reasoning": "Bandingkan daftar header dengan body yang sama pada kedua mode. Catat nilai dan cakupan setiap header; jangan menganggap CSP memperbaiki bug server-side yang terpisah.",
    },
    "host-reset-link": {
        "objectives": [
            "Memahami risiko menyusun absolute URL dari nilai host yang tidak tepercaya.",
            "Membedakan preview link dari email/token reset yang benar-benar diterbitkan.",
        ],
        "flow": "GET endpoint dengan parameter host -> evaluator memilih host input atau konstanta loopback -> JSON menampilkan resetLinkPreview.",
        "state": "Tidak mengirim email, menerbitkan token, mengubah password, atau menyentuh database. Token yang tampak adalah string TRAINING-ONLY.",
        "reasoning": "Gunakan training.invalid sebagai marker lokal teks; bandingkan host input dengan link preview dan flag. Secure memakai origin tetap; jangan mengikuti link atau mengarahkan request ke domain lain.",
    },
    "cache-poison": {
        "objectives": [
            "Memahami hubungan cache key, nilai yang dipakai untuk membentuk respons, dan isolasi cache.",
            "Membedakan prime dari read serta memeriksa variasi mode secara terpisah.",
        ],
        "flow": "action=prime menyimpan marker pada key session -> action=read mengambil marker -> evaluator menetapkan X-Cache HIT/MISS dan JSON hasil.",
        "state": "Cache simulasi berada dalam Flask session bertanda tangan, terpisah untuk kunci Vulnerable/Secure; bukan shared proxy/CDN dan tidak memengaruhi pengguna lain.",
        "reasoning": "Baca sebelum prime, prime satu marker teks, lalu read dalam sesi sama. Bandingkan marker dan X-Cache. Ganti mode dengan state bersih; Secure tidak boleh memakai cache rentan.",
    },
    "cache-deception": {
        "objectives": [
            "Memahami salah klasifikasi resource privat berdasarkan suffix path dan dampaknya terhadap kebijakan cache.",
            "Membaca Cache-Control bersama isi response, bukan hanya nama URL.",
        ],
        "flow": "GET endpoint membaca parameter path -> evaluator mengenali suffix .css/.js/.png -> membentuk body profile fixture -> menetapkan public max-age atau private no-store.",
        "state": "Tidak memakai database atau cache bersama; profile hanya string dummy pada response. Lab tidak menyimpan atau membagikan konten antar-user.",
        "reasoning": "Bandingkan /profile dengan /profile.css, ubah parameter saja. Temuan simulasi mensyaratkan body privat dummy sekaligus cacheable=true/public. Secure tetap private,no-store untuk keduanya.",
    },
    "websocket-auth": {
        "objectives": [
            "Memahami mengapa klaim autentikasi dari parameter klien tidak setara dengan identitas sesi server.",
            "Menganalisis keputusan akses pada handshake secara konseptual.",
        ],
        "flow": "GET endpoint membaca authenticated dari query -> Vulnerable memakai klaim tersebut, Secure melihat user_id sesi -> JSON mengembalikan authorized/event preview dan status.",
        "state": "Tidak membuka socket, tidak memakai database, dan tidak mengirim event jaringan. TRAINING_EVENT hanya string respons; Secure mengandalkan uid session yang sudah login.",
        "reasoning": "Bandingkan false dan true pada parameter; di Secure gunakan sesi anonim sebagai kontrol lalu sesi login lokal bila materi meminta. Periksa authorized/status/event. Jangan menyimpulkan bahwa WebSocket sungguhan dibuka.",
    },
    "graphql-object-access": {
        "objectives": [
            "Menguji kontrol akses per objek dengan principal sesi tetap dan ID fixture yang berbeda.",
            "Memahami bahwa bentuk mirip GraphQL tidak berarti endpoint menjalankan parser atau query GraphQL.",
        ],
        "flow": "POST form id -> evaluator memerlukan user_id sesi -> memetakan id 1 ke admin dan id 2 ke Budi -> Secure membandingkan pemilik dengan principal -> JSON profile atau error 404.",
        "state": "Menggunakan fixture hard-coded, tidak membaca GraphQL/database untuk objek ini. Login Budi diperlukan; ID admin hanya marker objek sintetis.",
        "reasoning": "Mulai dengan id=2 sebagai kontrol, ubah hanya id ke 1, lalu bandingkan username/displayLabel/status/flag. Secure menolak objek foreign. Jangan mengirim query GraphQL atau menebak ID lain.",
    },
    "nosql-filter": {
        "objectives": [
            "Memahami bagaimana operator filter yang diterima dapat mengubah semantik pencarian.",
            "Membedakan simulator grammar tetap dari database/query NoSQL sungguhan.",
        ],
        "flow": "GET filter -> evaluator membandingkan string role=user, role!=user, atau $ne:user -> membentuk matched/status/flag JSON menurut mode.",
        "state": "Tidak ada MongoDB, query dinamis, atau perubahan data. Fixture training-users dan nilai filter adalah string lokal; Secure mengizinkan bentuk yang ditetapkan dan menolak operator simulasi.",
        "reasoning": "Kirim role=user sebagai baseline lalu operator marker yang tertulis di materi. Amati matched, filter, status dan flag; Secure memberi 400 untuk operator. Jangan memperluas ke sintaks database lain.",
    },
    "xxe-sandbox": {
        "objectives": [
            "Memahami bagaimana deklarasi DOCTYPE/entity memengaruhi pemrosesan XML secara konseptual.",
            "Membedakan ekspansi fixture marker dari pembacaan file atau akses jaringan sungguhan.",
        ],
        "flow": "POST form xml -> evaluator mencari DOCTYPE dan marker training://marker -> mengembalikan konstanta KOPILAB_LOCAL_FIXTURE atau menolak DOCTYPE.",
        "state": "Tidak menjalankan parser eksternal, membuka file, atau membuat koneksi. externalAccess selalu false; marker dipetakan langsung ke string statis.",
        "reasoning": "Kirim XML biasa sebagai kontrol, lalu body latihan dari materi. Periksa parsed/expanded/externalAccess/status. Secure menolak DOCTYPE dengan 400 tetapi kasus XML biasa tetap menjadi kontrol positif.",
    },
    "ssti-toy": {
        "objectives": [
            "Mengenali perbedaan data teks dan ekspresi template yang dievaluasi server.",
            "Memahami batas evaluator marker tunggal dibanding template engine umum.",
        ],
        "flow": "GET name -> evaluator membandingkan persis marker {{7*7}} -> Vulnerable mengembalikan rendered=49; input lain atau Secure dikembalikan sebagai teks.",
        "state": "Tidak ada database, template engine dinamis, eval, atau akses object. Semua hasil berasal dari perbandingan string tetap.",
        "reasoning": "Kirim nama biasa sebagai baseline lalu satu marker yang ditetapkan. Bandingkan input/rendered/engine. Secure harus mempertahankan marker sebagai literal; angka 49 hanya simulasi tetap.",
    },
    "command-simulation": {
        "objectives": [
            "Memahami risiko pemisahan data dan command secara konseptual tanpa menjalankan proses sistem.",
            "Mengenali bahwa indikator output harus dibaca bersama jaminan batas simulator.",
        ],
        "flow": "GET value -> evaluator mencari substring marker statis -> membentuk preview marker atau mengembalikan nilai -> JSON selalu menyatakan simulated only.",
        "state": "Tidak ada shell, subprocess, filesystem, atau perubahan database. Output marker adalah konstanta; simulator tidak mengeksekusi input.",
        "reasoning": "Bandingkan coffee biasa dengan marker yang tercantum di materi. Lihat preview, input, dan execution. Jika statusnya simulated only, jangan mengartikan output sebagai hasil OS.",
    },
    "oauth-redirect": {
        "objectives": [
            "Memahami validasi callback sebagai pencocokan tujuan yang telah disetujui.",
            "Membedakan redirect preview fixture dari OAuth provider, token, dan alur autentikasi nyata.",
        ],
        "flow": "GET redirect_uri -> evaluator menerima path relatif atau satu URL simulator lokal pada Vulnerable -> JSON accepted/preview/tokenIssued; status 400 jika target tidak diterima.",
        "state": "Tidak ada provider, token, atau database. URL absolut yang diterima hanya callback latihan 127.0.0.1:9000; tokenIssued selalu false.",
        "reasoning": "Gunakan callback relatif sebagai baseline, lalu URL simulator tepat yang didokumentasikan. Periksa accepted, redirectPreview, tokenIssued, status, flag. Secure tetap menerima path relatif dan menolak URL absolut simulator.",
    },
    "oauth-state": {
        "objectives": [
            "Memahami state/nonce sebagai pengikat callback ke flow yang dimulai pada sesi browser yang sama.",
            "Menganalisis urutan begin-callback dan perilaku state mismatch/replay.",
        ],
        "flow": "GET begin=1 membuat state acak pada session -> callback mengirim state -> evaluator membandingkan dengan session via compare_digest -> menghapus state setelah callback.",
        "state": "State hidup di Flask session, bukan SQLite; providerContacted selalu false. Callback mengonsumsi state, sehingga pengulangan perlu memulai flow baru.",
        "reasoning": "Mulai dengan begin dan simpan respons di sesi yang sama, lalu bandingkan callback cocok/mismatch secara terkontrol. Secure menolak mismatch 400; jangan mencampur state dari mode atau sesi lain.",
    },
    "reset-host": {
        "objectives": [
            "Membedakan nilai host dari request dengan origin tepercaya yang seharusnya membentuk reset link.",
            "Memastikan preview link tidak disalahartikan sebagai pengiriman email atau penerbitan token.",
        ],
        "flow": "GET host -> evaluator memilih host input atau 127.0.0.1:5000 pada Secure -> membentuk linkPreview JSON.",
        "state": "Tidak menyentuh users, password, email, atau tabel token. tokenIssued/messageSent selalu false; hanya string preview fixture.",
        "reasoning": "Bandingkan default host dan training.invalid; amati linkPreview dan flag. Secure mengabaikan host input. Jangan buka link preview atau mengirim request ke host yang ditulis di parameter.",
    },
    "mfa-workflow": {
        "objectives": [
            "Memahami bahwa tahap complete tidak boleh menjadi pengganti challenge dan faktor yang tervalidasi.",
            "Menganalisis urutan transisi serta penggunaan challenge satu kali.",
        ],
        "flow": "POST action=status/begin/complete -> begin menyimpan challenge di session -> complete Secure mensyaratkan challenge dan code fixture -> respons stage/authenticated lalu challenge dihapus.",
        "state": "Hanya key session academy_mfa_challenge; tidak membuat autentikasi layanan nyata atau menulis database. Kode 424242 adalah fixture latihan.",
        "reasoning": "Periksa status awal, complete tanpa begin, lalu pada Secure begin diikuti complete dengan fixture code. Bandingkan stage/authenticated/status. Challenge yang selesai dikonsumsi; buat ulang sebelum tes berikutnya.",
    },
    "workflow-order": {
        "objectives": [
            "Memahami alur bisnis sebagai state machine dengan prasyarat antaraksi.",
            "Menguji apakah claim diterima hanya setelah verify dalam sesi yang sama.",
        ],
        "flow": "POST status/verify/claim -> verify menulis marker verified di session -> Secure claim memerlukan marker -> claim sukses menghapus marker.",
        "state": "State berada dalam Flask session, tanpa saldo, order, reward, atau database. Setiap sesi mempunyai state sendiri.",
        "reasoning": "Catat status awal, coba claim sebelum verify di Vulnerable, lalu bandingkan Secure. Jalur sah Secure adalah verify -> claim; jangan mengirim claim berulang setelah state dikonsumsi.",
    },
    "info-disclosure": {
        "objectives": [
            "Memahami prinsip minimisasi informasi dan perbedaan field publik dengan diagnostik internal.",
            "Menilai dampak berdasarkan data yang benar-benar terungkap, bukan label endpoint.",
        ],
        "flow": "GET view -> evaluator menentukan public atau diagnostic -> JSON menyertakan service dan, pada Vulnerable, object diagnostic dummy.",
        "state": "Tidak membaca secrets, konfigurasi host, file, atau database. debugHint/build adalah string fixture saja; Secure menetapkan diagnostic null.",
        "reasoning": "Bandingkan public dan diagnostic di kedua mode. Catat field yang muncul/hilang dan pastikan nilainya hanya fixture. Jangan mencoba nama view lain atau mencari data sistem.",
    },
    "http-parameter-pollution": {
        "objectives": [
            "Memahami bahwa parser dapat memilih nilai pertama/terakhir ketika parameter duplikat dikirim.",
            "Menguji validasi input ambigu dan interpretasi efektif aplikasi.",
        ],
        "flow": "GET amount -> framework mengumpulkan getlist('amount') -> evaluator menampilkan daftar, firstValue, effectiveValue (nilai terakhir) -> Secure menolak duplikat.",
        "state": "Tidak ada transaksi atau database; amount hanya ditampilkan sebagai string fixture. Duplikasi terlihat di query string dan tidak boleh digabung menjadi satu nilai.",
        "reasoning": "Mulai dengan satu amount=100, lalu kirim amount=1&amount=100. Bandingkan valuesReceived/first/effective. Secure memberi 400 sebelum memilih nilai; ini mendemonstrasikan parser aplikasi, bukan proxy eksternal.",
    },
    "tenant-export-chain": {
        "objectives": [
            "Mengikuti otorisasi objek pada tahap create dan download, bukan hanya endpoint pembuat job.",
            "Memahami principal session, tenant ownership, dan ID ekspor sebagai referensi, bukan izin.",
        ],
        "flow": "POST action=list/create/download -> login menghasilkan user_id session -> create memilih tenant dan menyimpan export ID/tenant di session -> download membaca job itu dan mengembalikan record fixture.",
        "state": "academy_tenant_exports berada di session Flask; bukan object storage atau tabel database. Budi (uid 2) memiliki tenant-campus; tenant-roastery adalah data sintetis.",
        "reasoning": "Buat dan unduh job sendiri sebagai baseline. Ubah hanya tenant saat create, lalu gunakan ID yang dikembalikan untuk download. Kebocoran terbukti pada records/tenant foreign; Secure harus menolak di create dan memeriksa ulang download.",
    },
    "checkout-settlement-chain": {
        "objectives": [
            "Memahami quote server sebagai sumber kebenaran harga dan settlement sebagai transisi state.",
            "Membedakan validasi nominal, pengikatan sesi, dan konsumsi quote satu kali.",
        ],
        "flow": "POST quote menyimpan id/total/used di session -> confirm mengambil quote aktif -> Vulnerable menerima submitted total; Secure membandingkannya dengan total server -> sukses menandai quote used.",
        "state": "academy_settlement_quote disimpan di session; tidak menulis orders/users atau mengurangi saldo. Total 125000 IDR adalah fixture.",
        "reasoning": "Lakukan quote -> confirm valid sebagai kontrol, lalu quote baru -> confirm total=1. Bandingkan submitted/server total, underpaid, status dan flag. Pada Secure uji mismatch 400, valid satu kali, lalu replay 409.",
    },
    "webhook-replay-chain": {
        "objectives": [
            "Memisahkan pemeriksaan authenticity marker dari idempotensi event.",
            "Mengamati bagaimana event ID duplikat dapat menggandakan efek simulasi.",
        ],
        "flow": "POST form + X-Training-Signature -> evaluator memeriksa event/amount fixture dan marker -> session menyimpan daftar event -> response memberi creditCount/duplicate.",
        "state": "Daftar event disimpan di session terpisah untuk mode Vulnerable dan Secure; tidak ada saldo atau integrasi webhook. fixture-valid bukan signature kriptografis.",
        "reasoning": "Kirim event valid sekali lalu replay request identik satu kali. Counter naik dan flag hanya pada duplikat Vulnerable; Secure menerima pertama lalu 409 tanpa menaikkan counter.",
    },
    "graphql-resolver-chain": {
        "objectives": [
            "Memahami bahwa otorisasi root/viewer tidak otomatis mengotorisasi invoice nested.",
            "Membedakan alias field dari identitas dan izin objek.",
        ],
        "flow": "POST viewer_id/invoice_id/alias -> login session memberi principal -> evaluator cocokkan viewer dengan principal -> cek invoice ID sendiri (dilewati Vulnerable, diwajibkan Secure) -> JSON field nested.",
        "state": "Record invoice 1/2 dan reference/total hard-coded; tidak ada parser GraphQL atau database. Budi uid 2; invoice admin hanya fixture.",
        "reasoning": "Baseline viewer=2/invoice=2, ubah alias sebagai kontrol, lalu ubah hanya invoice ke 1. Bukti adalah reference/total foreign. Secure memberi 404 tanpa data; status saja tidak cukup.",
    },
    "final-boss-ledger-chain": {
        "objectives": [
            "Menyusun hipotesis dari dua boundary yang berbeda: keutuhan harga saat settlement dan ownership saat receipt dibaca.",
            "Membedakan bukti di session dari bukti persisten di SQLite; mengukur perubahan orders dan users.balance.",
            "Menguji quote stale/lintas sesi, replay, dan penolakan atomik sebagai kontrol negatif.",
            "Membuktikan dampak rantai end-to-end tanpa menyimpulkan temuan hanya dari status sukses.",
        ],
        "flow": "Login menetapkan uid di Flask session -> POST map membaca products.id=1 dan users.balance -> quote membaca products.price, menyimpan record quote di final_boss_quotes dan mereferensikan quote_id di session -> settle mengunci transaksi, memeriksa dan mengonsumsi quote, memasukkan orders, serta mengurangi users.balance -> receipt mengambil orders.id. Vulnerable menerima total klien dan lookup receipt hanya berdasarkan id; Secure membandingkan total dengan quote serta menambahkan user_id principal pada lookup.",
        "state": "Flask session bertanda tangan menyimpan referensi quote_id dan bukti settlement, bukan otoritas total. final_boss_quotes menyimpan uid, produk, item, qty, total, dan status used; pembaruan used terjadi dalam transaksi settlement. Settlement juga menulis orders dan mengurangi users.balance secara atomik. Receipt hanya membaca tabel orders. Fixture produk 1 berharga Rp85.000; order 1 milik admin adalah fixture lintas-akun. Lab ini mengubah database lokal: gunakan akun seed dan reset database latihan bila ingin mengembalikan saldo/order.",
        "reasoning": "Mulai dari map dan receipt sendiri sebagai baseline. Buat quote baru, bandingkan serverTotal dengan nilai form, lalu submit total=1 sekali. Periksa orderId, orders.total, dan saldo sebelum/sesudah untuk membuktikan underpayment persisten. Baru sesudah itu minta receipt order_id=1; temuan akhir butuh ownerId berbeda dari principal serta settlement underpaid di sesi yang sama. Expert track menguji quote lama, quote pada sesi lain, replay, dan tidak adanya perubahan DB saat penolakan. Secure harus menolak mismatch sebelum INSERT/UPDATE dan mengembalikan 404 untuk receipt asing.",
    },
}
