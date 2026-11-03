"""Storefront, cart, review, wishlist, and order routes."""

from __future__ import annotations

import sqlite3
from html import escape

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from .. import require_login
from ..db import get_db
from ..inspector import record_query
from ..vulns.idor_order import get_order
from ..vulns.logic_balance import calculate_total, validate_checkout
from ..vulns.logic_price import client_price, order_note
from ..vulns.sqli_union import search_query
from ..vulns.xss import unsafe_html

shop_bp = Blueprint("shop", __name__)
COUPONS = {"HEMAT50": 50000}


@shop_bp.route("/")
def index():
    """Show the catalog and product review summaries."""
    record_query(
        """SELECT p.*, COUNT(r.id) AS review_count, COALESCE(ROUND(AVG(r.rating), 1), 5) AS rating
           FROM products p LEFT JOIN reviews r ON r.product_id=p.id
           WHERE p.id<99 GROUP BY p.id ORDER BY p.id"""
    )
    products = get_db().execute(
        """SELECT p.*, COUNT(r.id) AS review_count, COALESCE(ROUND(AVG(r.rating), 1), 5) AS rating
           FROM products p LEFT JOIN reviews r ON r.product_id=p.id
           WHERE p.id<99 GROUP BY p.id ORDER BY p.id"""
    ).fetchall()
    return render_template("shop/index.html", products=products)


@shop_bp.route("/search")
def search():
    """Search products using the intentionally injectable legacy query."""
    query_value = request.args.get("q", "")
    secure = session.get("secure_mode", False)
    sql = search_query(query_value, secure=secure)
    record_query(sql)
    error = None
    try:
        parameters = (f"%{query_value}%",) if secure else ()
        products = get_db().execute(sql, parameters).fetchall()
    except sqlite3.Error as database_error:
        products = []
        error = f"{database_error}"
    return render_template(
        "shop/search.html",
        query=escape(query_value) if secure else unsafe_html(query_value),
        products=products,
        error=error,
        sql=sql,
        image_for=image_for,
    )


@shop_bp.route("/product/<int:pid>")
def product(pid: int):
    """Show a product, reviews, and customer actions."""
    connection = get_db()
    product_row = connection.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if not product_row:
        return render_template(
            "error.html", code=404, title="Produk tidak ditemukan",
            message="Produk ini mungkin sudah tidak tersedia.",
        ), 404
    reviews = [
        dict(row)
        for row in connection.execute(
            "SELECT * FROM reviews WHERE product_id=? ORDER BY id DESC", (pid,)
        ).fetchall()
    ]
    for review_row in reviews:
        render_value = escape if session.get("secure_mode", False) else unsafe_html
        review_row["author"] = render_value(review_row["author"])
        review_row["body"] = render_value(review_row["body"])
    in_wishlist = False
    if session.get("uid"):
        in_wishlist = connection.execute(
            "SELECT 1 FROM wishlist WHERE user_id=? AND product_id=?",
            (session["uid"], pid),
        ).fetchone() is not None
    return render_template(
        "shop/product.html",
        product=product_row,
        reviews=reviews,
        in_wishlist=in_wishlist,
    )


@shop_bp.route("/review", methods=["POST"])
def review():
    """Save a product review and its rating."""
    product_id = int(request.form["pid"])
    rating = max(1, min(5, int(request.form.get("rating", 5))))
    connection = get_db()
    connection.execute(
        "INSERT INTO reviews(product_id,author,body,rating) VALUES(?,?,?,?)",
        (product_id, session.get("user", "anon"), request.form["body"], rating),
    )
    connection.commit()
    flash("Terima kasih, ulasanmu sudah tersimpan.", "success")
    return redirect(url_for("shop.product", pid=product_id))


@shop_bp.route("/cart", methods=["GET", "POST"])
def cart():
    """View or update the multi-item shopping cart."""
    current_cart = session.get("cart", {})
    if request.method == "POST":
        action = request.form.get("action", "add")
        product_id = request.form.get("product_id", "")
        if not product_id.isdigit():
            flash("Produk tidak valid.", "error")
            return redirect(url_for("shop.cart"))
        product_key = str(int(product_id))
        if action == "remove":
            current_cart.pop(product_key, None)
            flash("Produk dihapus dari keranjang.", "info")
        else:
            try:
                quantity = int(request.form.get("quantity", "1"))
            except ValueError:
                quantity = 0
            product_exists = get_db().execute(
                "SELECT 1 FROM products WHERE id=? AND id<99", (int(product_key),)
            ).fetchone()
            if not product_exists or not 1 <= quantity <= 25:
                flash("Pilih produk dan jumlah antara 1 sampai 25.", "error")
                return redirect(url_for("shop.cart"))
            if action == "update":
                current_cart[product_key] = quantity
                flash("Jumlah produk diperbarui.", "success")
            else:
                current_cart[product_key] = min(25, int(current_cart.get(product_key, 0)) + quantity)
                flash("Produk ditambahkan ke keranjang.", "success")
        session["cart"] = current_cart
        return redirect(url_for("shop.cart"))

    items, total = cart_items(current_cart)
    return render_template("shop/cart.html", items=items, total=total)


@shop_bp.route("/cart/checkout", methods=["POST"])
def cart_checkout():
    """Place all items in the cart using catalog prices."""
    response = require_login()
    if response:
        return response
    items, total = cart_items(session.get("cart", {}))
    if not items:
        flash("Keranjangmu masih kosong.", "error")
        return redirect(url_for("shop.cart"))
    connection = get_db()
    user = connection.execute("SELECT * FROM users WHERE id=?", (session["uid"],)).fetchone()
    if total > user["balance"]:
        flash("Saldo tidak cukup untuk menyelesaikan pesanan.", "error")
        return redirect(url_for("shop.cart"))
    last_order_id = 0
    for item in items:
        note = order_note(
            item["id"],
            current_app.config["FLAGS"]["logic-price"],
            secure=session.get("secure_mode", False),
        )
        cursor = connection.execute(
            "INSERT INTO orders(user_id,item,qty,total,note) VALUES(?,?,?,?,?)",
            (user["id"], item["name"], item["quantity"], item["subtotal"], note),
        )
        last_order_id = cursor.lastrowid
    connection.execute("UPDATE users SET balance=balance-? WHERE id=?", (total, user["id"]))
    connection.commit()
    session["cart"] = {}
    flash(f"Pesanan berhasil dibuat. Total Rp {total:,}.", "success")
    return redirect(url_for("shop.order", oid=last_order_id))


@shop_bp.route("/checkout", methods=["POST"])
def checkout():
    """Create a legacy lab order using the client-controlled price."""
    response = require_login()
    if response:
        return response
    pid = int(request.form["pid"])
    quantity = int(request.form.get("qty", 1))
    coupons = request.form.getlist("coupon")
    secure = session.get("secure_mode", False)
    if secure and not validate_checkout(quantity, coupons, COUPONS):
        return render_template(
            "error.html", code=400, title="Pesanan tidak valid",
            message="Jumlah harus positif dan kupon harus valid serta tidak boleh digunakan berulang.",
        ), 400
    connection = get_db()
    product_row = connection.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if not product_row:
        return render_template(
            "error.html", code=404, title="Produk tidak ditemukan",
            message="Produk ini mungkin sudah tidak tersedia.",
        ), 404
    price = client_price(request.form["price"], product_row["price"] if secure else None)
    record_query("SELECT * FROM products WHERE id=?")
    total = calculate_total(price, quantity, coupons, COUPONS)
    user = connection.execute("SELECT * FROM users WHERE id=?", (session["uid"],)).fetchone()
    if total > user["balance"]:
        flash("Saldo tidak cukup.", "error")
        return redirect(url_for("shop.product", pid=pid))
    note = order_note(pid, current_app.config["FLAGS"]["logic-price"], secure=secure)
    cursor = connection.execute(
        "INSERT INTO orders(user_id,item,qty,total,note) VALUES(?,?,?,?,?)",
        (user["id"], product_row["name"], quantity, total, note),
    )
    connection.execute("UPDATE users SET balance=balance-? WHERE id=?", (total, user["id"]))
    connection.commit()
    return render_template(
        "shop/order_complete.html",
        order_id=cursor.lastrowid,
        total=total,
        flag=note if pid == 99 else None,
    )


@shop_bp.route("/order/<int:oid>")
def order(oid: int):
    """Show an order without enforcing ownership in the vulnerable lab."""
    response = require_login()
    if response:
        return response
    owner_id = session["uid"] if session.get("secure_mode", False) else None
    record_query(
        "SELECT * FROM orders WHERE id=?" + (" AND user_id=?" if owner_id else "")
    )
    order_row = get_order(get_db(), oid, owner_id)
    if not order_row:
        return render_template(
            "error.html", code=404, title="Pesanan tidak ditemukan",
            message="Nomor pesanan tidak ditemukan.",
        ), 404
    return render_template("shop/order.html", order=order_row)


@shop_bp.route("/wishlist")
def wishlist():
    """Show the signed-in user's saved products."""
    response = require_login()
    if response:
        return response
    products = get_db().execute(
        """SELECT p.* FROM products p JOIN wishlist w ON w.product_id=p.id
           WHERE w.user_id=? ORDER BY p.name""",
        (session["uid"],),
    ).fetchall()
    return render_template("shop/wishlist.html", products=products)


@shop_bp.route("/wishlist/<int:pid>", methods=["POST"])
def wishlist_toggle(pid: int):
    """Toggle a product in the signed-in user's wishlist."""
    response = require_login()
    if response:
        return response
    connection = get_db()
    existing = connection.execute(
        "SELECT 1 FROM wishlist WHERE user_id=? AND product_id=?", (session["uid"], pid)
    ).fetchone()
    if existing:
        connection.execute("DELETE FROM wishlist WHERE user_id=? AND product_id=?", (session["uid"], pid))
        flash("Produk dihapus dari wishlist.", "info")
    else:
        product_exists = connection.execute(
            "SELECT 1 FROM products WHERE id=? AND id<99", (pid,)
        ).fetchone()
        if not product_exists:
            return render_template(
                "error.html", code=404, title="Produk tidak ditemukan",
                message="Produk ini mungkin sudah tidak tersedia.",
            ), 404
        connection.execute(
            "INSERT INTO wishlist(user_id,product_id) VALUES(?,?)", (session["uid"], pid)
        )
        flash("Produk disimpan di wishlist.", "success")
    connection.commit()
    return redirect(url_for("shop.product", pid=pid))


def cart_items(cart: dict[str, int]) -> tuple[list[dict[str, object]], int]:
    """Build the cart display and subtotal from current catalog data."""
    if not cart:
        return [], 0
    connection = get_db()
    items: list[dict[str, object]] = []
    total = 0
    for product_id, quantity in cart.items():
        if not str(product_id).isdigit() or not isinstance(quantity, int):
            continue
        row = connection.execute(
            "SELECT * FROM products WHERE id=? AND id<99", (int(product_id),)
        ).fetchone()
        if not row:
            continue
        subtotal = row["price"] * quantity
        items.append({**dict(row), "quantity": quantity, "subtotal": subtotal})
        total += subtotal
    return items, total


def image_for(product_id: int) -> str:
    """Select a bundled SVG illustration for a catalog item."""
    if product_id == 99:
        return "special-mug.svg"
    if 11 <= product_id <= 15:
        return "brewing-gear.svg"
    return "coffee-bag.svg"
