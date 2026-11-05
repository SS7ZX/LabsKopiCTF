# Burp Repeater wajib: mass assignment profil

## Tujuan
Wajib menggunakan Burp Suite Repeater untuk menangkap, mengulang, dan membandingkan request profil pada endpoint latihan lokal. Temukan apakah server mempercayai field `role` yang tidak disediakan oleh form.

## Konsep
Mass assignment terjadi ketika server mengikat field request langsung ke atribut internal objek tanpa allowlist yang ketat. Form hanya menawarkan email, tetapi pengguna mengendalikan request HTTP dan dapat menambahkan field. Informasi identitas dari sesi harus menentukan akun yang diubah; role harus ditentukan oleh kebijakan server, bukan nilai dari browser. Latihan ini terbatas pada akun Budi dan database KopiLab di komputer sendiri.

## Analisis Mendalam
- **Batas kepercayaan:** browser dan seluruh field request adalah input yang dapat diubah. Menyembunyikan field dari HTML bukan kontrol keamanan.
- **Alur data:** `POST /extra/burp-profile` membaca form, lalu memanggil fungsi pembaruan profil. Periksa bagaimana data diteruskan dari `request.form` ke kolom database; bandingkan daftar atribut yang boleh diedit dengan atribut yang benar-benar diterima.
- **Sumber identitas:** akun yang diperbarui harus berasal dari `session["uid"]`. Jangan menganggap nilai akun atau role yang dikirim klien sebagai identitas yang sah.
- **Sinyal respons:** bandingkan status HTTP, email dan role pada JSON, serta header `X-Lab-Flag`. Status sukses saja tidak membuktikan bahwa perubahan yang diminta benar-benar terjadi.
- **Dampak:** jika role klien diterima, akun pelanggan lokal dapat memperoleh hak admin. Ini menunjukkan dampak kontrol akses; jangan gunakan teknik ini pada akun atau sistem di luar lab.
- **Perbandingan aman:** Secure mode menerima pembaruan email yang sah tetapi mengabaikan role dari request. Ulangi request yang sama dan verifikasi keadaan di respons, bukan hanya pesan visual.

## Hint 1
Form target hanya menampilkan `email`. Tangkap pengiriman normal dan lihat bagian body request sebelum mengubah apa pun.

## Hint 2
Di Burp, gunakan **Send to Repeater** dari HTTP history. Ulangi request normal lebih dahulu agar kamu punya baseline untuk membandingkan respons.

## Hint 3
Pada salinan request Repeater ke endpoint lab saja, tambahkan field form `role` dengan nilai `admin`. Flag ada di header respons jika mode Vulnerable menerima perubahan.

## Solusi
Masuk sebagai Budi, buka `/extra/burp-profile`, tangkap submit form email di Burp Proxy, dan kirim request tersebut ke Repeater. Kirim baseline; respons menunjukkan role `user` dan tidak memiliki flag. Tambahkan `&role=admin` ke body form-urlencoded di Repeater, lalu kirim hanya ke `127.0.0.1:5000/extra/burp-profile`. Dalam mode Vulnerable respons menunjukkan role `admin` dan header `X-Lab-Flag`. Ulangi dengan request baru saat mode Secure aktif: role tetap `user` dan header flag tidak ada.

## Akar Masalah
Handler mengirim field request ke helper pembaruan generik. Tanpa allowlist berdasarkan atribut yang memang boleh diedit, field internal seperti `role` ikut dianggap sebagai masukan profil biasa. Validasi form HTML hanya mengatur tampilan browser dan tidak membatasi request yang diterima server.

## Perbaikan
Tetapkan allowlist server-side untuk atribut yang bisa diubah pengguna, misalnya hanya `email`; ikat nilai ke ID pengguna dari sesi; jangan pernah memperbarui role melalui handler profil; dan uji bahwa field tambahan ditolak atau diabaikan. Untuk perubahan role yang sah, gunakan alur admin terpisah dengan otorisasi eksplisit dan audit.

## Contoh Rentan
```python
update_profile(connection, request.form.items(), session["uid"], secure=False)
```

## Contoh Aman
```python
allowed_fields = {"email": request.form["email"]}
update_profile(connection, allowed_fields.items(), session["uid"], secure=True)
```

## Langkah Latihan
1. Pastikan KopiLab berjalan di komputer sendiri melalui `python run.py`, lalu buka <http://127.0.0.1:5000>. Jangan gunakan alamat host lain atau expose port server.
2. Mulai dalam mode **Vulnerable**. Buka halaman login di browser Burp dan masuk sebagai Budi (`budi` / `budi123`). Jangan kirim kredensial latihan ke host selain KopiLab lokal.
3. Di browser yang dibuka melalui Burp, kunjungi <http://127.0.0.1:5000/extra/burp-profile>. Pastikan halaman menampilkan form email dan role saat ini `user`.
4. Di Burp, buka **Proxy → Intercept** dan pastikan **Intercept is off**. Isi email latihan yang valid, lalu tekan **Simpan profil latihan**. Ini menghasilkan request normal yang dapat diamati tanpa menghentikan browser.
5. Buka **Proxy → HTTP history**. Pilih request `POST` ke host `127.0.0.1`, port `5000`, path `/extra/burp-profile`. Pastikan request yang dipilih berasal dari submit form barusan, bukan file CSS atau request lain.
6. Di panel request, identifikasi method, path, `Content-Type`, dan body form. Baseline semestinya membawa field `email` saja. Header `Cookie` membawa sesi—jangan menyalin nilainya ke laporan, chat, atau tempat publik.
7. Catat response baseline. Perhatikan status HTTP, role `user` pada JSON, dan tidak adanya `X-Lab-Flag`. Ini pembanding untuk percobaan berikut.
8. Klik kanan request di HTTP history dan pilih **Send to Repeater**. Buka tab **Repeater**, periksa bahwa host serta path masih tepat menuju KopiLab lokal, lalu tekan **Send** tanpa mengubah request. Pastikan hasilnya konsisten dengan baseline.
9. Pada body form-urlencoded di Repeater, pertahankan email dan tambahkan field `role=admin` dengan pemisah `&`. Jangan mengubah host, port, path, atau cookie. Burp biasanya memperbarui `Content-Length` saat request dikirim.
10. Tekan **Send** sekali. Baca response lengkap: status, JSON, dan headers. Jika eksperimen diterima pada mode Vulnerable, role menjadi `admin` dan header `X-Lab-Flag` berisi flag lab.
11. Salin flag dari header respons ke kotak submit flag pada halaman lab KopiLab. Jangan menaruh cookie sesi ke laporan atau submit flag dari lab lain.
12. Untuk menguji perbaikan, buka KopiLab dan ganti ke mode **Secure**. Tangkap ulang request form dari browser Burp setelah pergantian mode, lalu kirim request terbaru ke Repeater agar cookie sesi mencerminkan mode sekarang. Jangan memakai cookie lama.
13. Ulangi perubahan `role=admin` hanya pada request lab ini. Secure mode seharusnya tetap merespons role `user` dan tidak memberikan header flag. Email tetap boleh berubah karena itu field profil yang diizinkan.
14. Catat perbedaan sebelum dan sesudah: field yang dikirim, field yang diproses, role pada response, serta ada/tidaknya header flag. Setelah memahami dampak, reset database lokal dari halaman Labs agar akun Budi kembali ke kondisi awal.

## Bukti yang Dicatat
- URL target harus `http://127.0.0.1:5000/extra/burp-profile`; jangan menyimpan request ke target lain.
- Baseline: method/path, field email saja, status, role `user`, dan tidak adanya header flag.
- Request Repeater yang dimodifikasi: field `role=admin`; rahasiakan header `Cookie` dan data sesi.
- Mode Vulnerable: role pada response dan header `X-Lab-Flag` sebagai bukti dampak.
- Mode Secure: role tetap `user`, tidak ada flag, dan email yang diizinkan tetap dapat diperbarui.
- Root cause dan rekomendasi: allowlist field pada server serta identitas akun bersumber dari sesi.

## Kalau Masih Bingung
Pastikan request yang dipilih adalah `POST /extra/burp-profile`, bukan request login atau request halaman. Kirim dahulu body baseline tanpa perubahan; setelah itu edit salinan di Repeater. Jika browser tertahan, buka Intercept dan klik **Forward**. Jika role sudah berubah, gunakan tombol reset database lokal di Labs sebelum mengulang.
