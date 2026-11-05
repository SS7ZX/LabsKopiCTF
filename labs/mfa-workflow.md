# MFA: melewati langkah verifikasi simulasi

## Tujuan
Menguji apakah server menegakkan urutan autentikasi multi-langkah dan bukan hanya menerima klaim akhir klien.

## Konsep
MFA memerlukan faktor tambahan yang diverifikasi server. Memanggil langkah “complete” tidak boleh menggantikan challenge yang sah. Endpoint ini hanya memodelkan state di session KopiLab dan memakai kode fixture `424242`; tidak membuat sesi autentikasi nyata untuk layanan lain.

## Hint 1
Mulai dengan melihat stage `start`.

## Hint 2
Vulnerable menerima `action=complete` tanpa challenge.

## Hint 3
Secure harus melihat challenge session dan kode fixture yang cocok.

## Solusi
POST `action=complete` tanpa memulai challenge memberi authenticated pada Vulnerable, tetapi 403 pada Secure.

## Akar Masalah
Handler akhir tidak memastikan tahap/faktor sebelumnya berhasil.

## Perbaikan
Simpan state challenge di server, ikat ke sesi dan akun, batasi percobaan, kedaluwarsakan, dan konsumsi challenge sekali pakai.

## Contoh Rentan
Mempercayai field `action=complete` sebagai bukti MFA.

## Contoh Aman
Verifikasi challenge aktif dan proof yang cocok sebelum transisi ke authenticated.

## Analisis Mendalam
- Request harus POST form-urlencoded ke endpoint lokal.
- Simulasikan bypass sebelum memulai challenge.
- Secure diuji dengan challenge baru dan kode fixture; state tersimpan per session.
- Perhatikan stage, authenticated, status, serta penggunaan ulang challenge.
- Ini bukan login provider atau TOTP sungguhan.

## Langkah Latihan
1. Pada Vulnerable kirim `action=complete` tanpa code.
2. Catat response `authenticated` dan flag.
3. Aktifkan Secure lewat UI, lalu tangkap request baru.
4. Coba complete tanpa begin; Secure harus mengembalikan 403.
5. POST `action=begin`, kemudian POST `action=complete&code=424242` pada sesi sama.
6. Pastikan hanya alur yang benar menyelesaikan fixture.

## Bukti yang Dicatat
Action, stage, status, authenticated, urutan request, mode. Jangan kirim cookie atau kode di luar lingkungan lokal.

## Kalau Masih Bingung
Gunakan dua request Secure secara berurutan: begin lalu complete. Repeater perlu memakai session browser yang sama.
