"""SQLite setup and connection helpers."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Open a row-addressable SQLite connection for the active app."""
    if "database" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        g.database = connection
    return g.database


def close_db(_: BaseException | None = None) -> None:
    """Close the current request's SQLite connection."""
    connection = g.pop("database", None)
    if connection is not None:
        connection.close()


def init_db(app: Any, reset: bool = False) -> None:
    """Create or migrate the schema and seed KopiLab training data."""
    database = Path(app.config["DATABASE"])
    database.parent.mkdir(parents=True, exist_ok=True)
    files_dir = Path(app.config["FILES_DIR"])
    files_dir.mkdir(parents=True, exist_ok=True)
    (files_dir / "welcome.txt").write_text("Selamat datang di KopiLab.\n", encoding="utf-8")
    (Path(app.config["PROJECT_DIR"]) / "secret.txt").write_text(
        app.config["FLAGS"]["traversal"] + "\n", encoding="utf-8"
    )
    if reset and database.exists():
        os.remove(database)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, role TEXT, balance INTEGER);
            CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, name TEXT, price INTEGER, description TEXT, category TEXT NOT NULL DEFAULT 'Kopi', image TEXT NOT NULL DEFAULT 'coffee-bag.svg');
            CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, user_id INTEGER, item TEXT, qty INTEGER, total INTEGER, note TEXT);
            CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY, product_id INTEGER, author TEXT, body TEXT);
            CREATE TABLE IF NOT EXISTS secrets(name TEXT, value TEXT);
            CREATE TABLE IF NOT EXISTS wishlist(user_id INTEGER NOT NULL, product_id INTEGER NOT NULL, UNIQUE(user_id, product_id));
            CREATE TABLE IF NOT EXISTS password_reset_tokens(user_id INTEGER PRIMARY KEY, token_hash TEXT NOT NULL, expires_at INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS lab_solves(player_id TEXT NOT NULL, lab_id TEXT NOT NULL, solved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(player_id, lab_id));
            CREATE TABLE IF NOT EXISTS request_inspector(player_id TEXT PRIMARY KEY, method TEXT NOT NULL, path TEXT NOT NULL, sql_text TEXT NOT NULL, response_headers TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS coupon_redemptions(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, coupon TEXT NOT NULL, redeemed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS login_attempts(player_id TEXT PRIMARY KEY, attempts INTEGER NOT NULL DEFAULT 0, last_attempt INTEGER NOT NULL DEFAULT 0);
            """
        )
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(reviews)")}
        if "rating" not in columns:
            connection.execute("ALTER TABLE reviews ADD COLUMN rating INTEGER NOT NULL DEFAULT 5")
        product_columns = {row["name"] for row in connection.execute("PRAGMA table_info(products)")}
        if "category" not in product_columns:
            connection.execute("ALTER TABLE products ADD COLUMN category TEXT NOT NULL DEFAULT 'Kopi'")
        if "image" not in product_columns:
            connection.execute("ALTER TABLE products ADD COLUMN image TEXT NOT NULL DEFAULT 'coffee-bag.svg'")

        connection.executemany(
            "INSERT OR IGNORE INTO users(id,username,password,email,role,balance) VALUES(?,?,?,?,?,?)",
            [
                (1, "admin", "Adm1n!Sup3r#x", "admin@kopilab.local", "admin", 0),
                (2, "budi", "budi123", "budi@mail.local", "user", 500000),
                (3, "siti", "siti123", "siti@mail.local", "user", 500000),
            ],
        )
        connection.executemany(
            "INSERT OR IGNORE INTO products(id,name,price,description) VALUES(?,?,?,?)",
            [
                (1, "Kopi Gayo 250g", 85000, "Aceh Gayo, medium roast"),
                (2, "Kopi Toraja 250g", 95000, "Sulawesi, fruity"),
                (3, "Kopi Flores 250g", 90000, "Flores Bajawa, chocolatey"),
                (4, "V60 Dripper", 120000, "Keramik, ukuran 02"),
                (5, "Grinder Manual", 450000, "Burr stainless"),
                (6, "Kopi Kintamani 250g", 88000, "Bali, citrus dan floral"),
                (7, "Kopi Kerinci 250g", 92000, "Jambi, manis dengan body tebal"),
                (8, "Kopi Papua Wamena 250g", 105000, "Highland, lembut dan seimbang"),
                (9, "Kopi Java Preanger 250g", 82000, "Jawa Barat, aroma rempah"),
                (10, "Kopi Sidikalang 250g", 87000, "Sumatera Utara, bold roast"),
                (11, "French Press 600ml", 185000, "Kaca borosilikat dan filter baja"),
                (12, "Gooseneck Kettle", 325000, "Leher angsa, kapasitas 600ml"),
                (13, "Timemore Scale", 590000, "Timbangan digital untuk seduh"),
                (14, "Server Kaca 500ml", 145000, "Kaca tahan panas dengan skala"),
                (15, "Filter Paper V60", 45000, "Isi 100 lembar, ukuran 02"),
                (99, "Secret Mug", 999999999, "Edisi terbatas. Cuma buat sultan."),
            ],
        )
        connection.execute(
            """UPDATE products SET
               category=CASE WHEN id BETWEEN 11 AND 15 THEN 'Alat seduh'
                             WHEN id=99 THEN 'Edisi khusus' ELSE 'Kopi nusantara' END,
               image=CASE WHEN id BETWEEN 11 AND 15 THEN 'brewing-gear.svg'
                          WHEN id=99 THEN 'special-mug.svg' ELSE 'coffee-bag.svg' END"""
        )
        connection.execute(
            "INSERT OR IGNORE INTO orders(id,user_id,item,qty,total,note) VALUES(1,1,'Kopi Gayo 250g',1,85000,?)",
            ("Catatan internal: " + app.config["FLAGS"]["idor-order"],),
        )
        connection.execute(
            "INSERT OR IGNORE INTO orders(id,user_id,item,qty,total,note) VALUES(2,2,'V60 Dripper',1,120000,'Tolong kirim pagi')"
        )
        connection.execute(
            "INSERT OR IGNORE INTO orders(id,user_id,item,qty,total,note) VALUES(3,3,'Kopi Toraja 250g',2,190000,'-')"
        )
        connection.execute(
            "INSERT INTO secrets(name,value) SELECT 'flag',? WHERE NOT EXISTS (SELECT 1 FROM secrets WHERE name='flag')",
            (app.config["FLAGS"]["sqli-union"],),
        )
        connection.execute(
            "INSERT OR IGNORE INTO reviews(id,product_id,author,body,rating) VALUES(1,1,'budi','Mantap, aromanya kuat.',5)"
        )
        connection.commit()
    finally:
        connection.close()
