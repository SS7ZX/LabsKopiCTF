"""Start KopiLab on loopback only."""

import sys

from kopilab import create_app
from kopilab.db import init_db
from kopilab.internal_service import start_internal_service

app = create_app()


def main() -> None:
    """Run the local server, optionally recreating its training database."""
    if "--reset" in sys.argv:
        init_db(app, reset=True)
    start_internal_service(app)
    print("KopiLab: http://127.0.0.1:5000 (internal lab service: 127.0.0.1:5001)")
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
