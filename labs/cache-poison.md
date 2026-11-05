# Cache poisoning simulasi per sesi

## Tujuan
Memahami bagaimana cache yang menggunakan key tidak lengkap bisa menyajikan variasi response yang keliru.

## Konsep
Cache poisoning terjadi bila cache menyimpan response berdasarkan key yang tidak mencakup input yang memengaruhi response. Simulasi KopiLab menyimpan marker hanya di session browser—tidak ada shared cache, pengguna lain, atau proxy cache.

## Hint 1
Kirim `action=read` dahulu untuk melihat nilai awal.

## Hint 2
Gunakan `action=prime&marker=...`, kemudian baca lagi dalam sesi yang sama.

## Hint 3
Perhatikan `X-Cache` dan field `cached`; marker adalah teks fixture, bukan HTML yang dijalankan.

## Solusi
Vulnerable menyimpan marker latihan ke state sesi lalu mengembalikannya pada read berikutnya. Secure tidak mem-prime variasi tersebut.

## Akar Masalah
Simulasi rentan menggunakan cache key yang tidak mengikat variasi marker.

## Perbaikan
Rancang cache key dari seluruh input yang relevan, jangan menyimpan response privat ke cache bersama, dan tetapkan kebijakan cache yang sesuai.

## Contoh Rentan
Menyimpan semua variasi response pada satu key generik.

## Contoh Aman
Gunakan key yang mencakup variasi aman dan pisahkan cache per konteks pengguna.

## Analisis Mendalam
- Ini state per browser session, bukan Redis/CDN/proxy global.
- Baseline `read` harus dijalankan sebelum `prime`.
- `prime` mengubah session; request `read` kedua adalah bukti persistensi simulasi.
- `X-Cache` hanya indikator fixture.
- Secure tidak membiarkan marker berbahaya masuk ke cache dan tetap memberi output default.

## Langkah Latihan
1. Buka `/extra/academy/cache-poison?action=read` lewat browser Burp.
2. Kirim request ke Repeater dan catat `cached` serta `X-Cache`.
3. Ubah action menjadi `prime` dan marker menjadi `kopilab-latihan`; kirim satu kali.
4. Kirim `action=read` dalam sesi sama dan amati marker.
5. Ganti mode Secure, tangkap request baru, lalu ulangi pada sesi/mode itu. Secure tidak boleh memunculkan marker yang di-prime.

## Bukti yang Dicatat
Action, marker dummy, X-Cache, nilai cached/read, mode. Jangan bagikan cookie sesi.

## Kalau Masih Bingung
Gunakan urutan read → prime → read. Semua request harus mempertahankan sesi browser yang sama.
