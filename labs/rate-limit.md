# Batas percobaan login

## Tujuan
Memahami mengapa endpoint autentikasi perlu pembatasan percobaan yang hati-hati.

## Konsep
Percobaan login berulang dapat meningkatkan risiko tebakan kredensial. Lab ini menggunakan counter non-destruktif per pelajar dan tidak mencoba password akun.

## Hint 1
Kirim request gagal berulang ke endpoint khusus simulasi.

## Hint 2
Bandingkan respons setelah beberapa request dalam mode berbeda.

## Hint 3
Endpoint tidak mengautentikasi pengguna dan tidak menebak password.

## Solusi
Kirim enam POST ke endpoint latihan dan amati bahwa mode vulnerable tidak membatasi jumlah.

## Akar masalah
Mode vulnerable mencatat percobaan tanpa cooldown atau batas.

## Perbaikan
Rate-limit berdasarkan beberapa sinyal, gunakan backoff, pemantauan, dan pesan yang tidak membocorkan keberadaan akun.

## Contoh rentan
Counter bertambah terus tanpa penolakan.

## Contoh aman
Batas percobaan sementara dengan cooldown yang terukur dan pemulihan setelah jangka waktu tertentu.

## Langkah latihan
1. Endpoint ini hanya mencatat percobaan simulasi; ia tidak mencoba username atau password.
2. Kirim POST ke `/extra/rate-login` enam kali pada sesi browser KopiLab yang sama.
3. Mode **Vulnerable** terus menaikkan hitungan. Perhatikan header flag pada respons setelah percobaan keenam.
4. Aktifkan **Secure** dan ulangi pada sesi bersih. Setelah batas tercapai, server menjawab HTTP 429.

## Kalau masih bingung
Rate limit seperti batas percobaan PIN di mesin ATM. Tujuannya bukan menebak password untukmu, tetapi memperagakan bahwa server harus memperlambat percobaan berulang.
