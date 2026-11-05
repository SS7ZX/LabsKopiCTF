# OAuth state parameter simulasi

## Tujuan
Melihat fungsi parameter state dalam mengikat callback otorisasi dengan browser/session yang memulai alur.

## Konsep
Nilai state acak membantu mencegah callback yang tidak terkait dimasukkan ke alur login pengguna. Endpoint ini menggunakan provider fiktif lokal; tidak ada akun OAuth nyata atau token yang diterbitkan.

## Hint 1
Mulai dengan `begin=1` untuk membuat state fixture sesi.

## Hint 2
Uji callback tanpa state hanya pada mode Vulnerable.

## Hint 3
Secure membandingkan state callback dengan nilai sesi dan mengonsumsi state sekali.

## Solusi
Vulnerable menerima callback tanpa pencocokan state. Secure mensyaratkan state yang dibuat pada sesi saat ini.

## Akar Masalah
Callback tidak diikat ke permintaan otorisasi yang memulainya.

## Perbaikan
Buat state acak per alur, simpan/ikat ke sesi, bandingkan secara aman, dan invalidasi sesudah callback.

## Contoh Rentan
Memproses callback meski parameter state hilang atau tidak cocok.

## Contoh Aman
Tolak callback kecuali state acak sesuai dengan nilai sekali-pakai pada sesi.

## Analisis Mendalam
- `begin=1` menghasilkan state khusus session demo.
- Dalam Secure, tangkap nilai dari response sendiri dan jangan membagikannya.
- Callback mengembalikan accepted/stateMatched/providerContacted.
- State mismatch harus ditolak di Secure dan tidak menghubungi provider.
- Repeater harus menggunakan sesi yang sama untuk menguji lifecycle state.

## Langkah Latihan
1. Kirim GET `/extra/academy/oauth-state?begin=1` pada browser Burp.
2. Catat state secara lokal saja; jangan tempel ke chat atau screenshot.
3. Kirim callback tanpa `state` melalui Repeater pada Vulnerable; amati hasil.
4. Aktifkan Secure dan mulai flow baru untuk memperoleh state baru.
5. Uji callback tanpa state, lalu bila perlu gunakan state flow Secure yang sama satu kali.
6. Pastikan mismatch ditolak dan callback valid mengonsumsi state.

## Bukti yang Dicatat
Flow dimulai, state cocok/tidak cocok (tanpa nilai token), accepted, status, providerContacted=false, mode.

## Kalau Masih Bingung
Secure memerlukan urutan begin → callback pada session browser yang sama. Jangan gunakan nilai dari sesi lama.
