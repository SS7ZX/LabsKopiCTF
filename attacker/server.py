"""Small local-only simulator page for browser-based security lessons."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PAGE = """<!doctype html>
<html lang="id"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>KopiLab Local Simulator</title>
<style>
body{max-width:760px;margin:3rem auto;padding:0 1rem;font:16px/1.6 system-ui;color:#29241f}
main{padding:1.5rem;border:1px solid #ddd3c6;border-radius:12px;background:#fff}
.notice{padding:.8rem;background:#fff0cf;border-radius:8px;color:#69450e}
label{display:block;margin:.8rem 0}input,button{padding:.6rem;font:inherit}
</style>
<main><p class="notice"><strong>Simulator lokal KopiLab.</strong> Hanya arahkan ke
127.0.0.1:5000 milik KopiLab. Tidak ada layanan eksternal yang digunakan.</p>
<h1>Form demo CSRF</h1>
<p>Form ini hanya mengirim nilai yang kamu pilih ke endpoint transfer lokal untuk
menjelaskan efek request lintas port pada browser.</p>
<form method="post" action="http://127.0.0.1:5000/transfer">
<label>Penerima latihan <input name="to" value="siti"></label>
<label>Jumlah latihan <input name="amount" type="number" value="1"></label>
<button type="submit">Kirim request demo ke KopiLab lokal</button></form>
<h2>Pelajaran XSS</h2>
<p>Untuk XSS, kunjungi halaman pencarian atau ulasan KopiLab dan bandingkan
mode Vulnerable dengan Secure. Simulator ini tidak membaca cookie atau mengirim
data ke tempat lain.</p>
<p><a href="http://127.0.0.1:5000/labs">Kembali ke lab KopiLab</a></p>
</main></html>"""


class SimulatorHandler(BaseHTTPRequestHandler):
    """Serve a fixed safe page for the local browser simulator."""

    def do_GET(self) -> None:
        """Return the static simulator content."""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(PAGE.encode("utf-8"))

    def log_message(self, format_string: str, *args: object) -> None:
        """Keep local simulator access logs quiet."""


def main() -> None:
    """Bind the standalone simulator only to loopback."""
    server = ThreadingHTTPServer(("127.0.0.1", 9000), SimulatorHandler)
    print("KopiLab simulator: http://127.0.0.1:9000 (local only)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
