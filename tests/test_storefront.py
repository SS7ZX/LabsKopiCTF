"""Tests for the storefront introduced in milestone M2."""


def test_homepage_renders_product_grid_and_local_assets(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Temukan ritual seduh favoritmu" in response.data
    assert b"product-grid" in response.data
    assert b"/static/css/style.css" in response.data
    assert b"https://" not in response.data


def test_database_seeds_catalog_and_ratings(client, app):
    from kopilab.db import get_db

    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM products WHERE id<99").fetchone()[0] >= 15
        assert "rating" in {row["name"] for row in get_db().execute("PRAGMA table_info(reviews)")}


def test_product_page_shows_review_and_wishlist_action(client):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    response = client.get("/product/1")
    assert response.status_code == 200
    assert b"Mantap, aromanya kuat." in response.data
    assert b"Simpan ke wishlist" in response.data


def test_cart_supports_multiple_items_and_checkout(client):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    client.post("/cart", data={"action": "add", "product_id": "1", "quantity": "2"})
    client.post("/cart", data={"action": "add", "product_id": "4", "quantity": "1"})
    cart_response = client.get("/cart")
    assert b"Kopi Gayo 250g" in cart_response.data
    assert b"V60 Dripper" in cart_response.data
    assert client.post("/cart/checkout").status_code == 302
    orders = client.get("/orders")
    assert b"Kopi Gayo 250g" in orders.data
    assert b"V60 Dripper" in orders.data


def test_wishlist_persists_to_sqlite(client):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    client.post("/wishlist/1")
    response = client.get("/wishlist")
    assert b"Kopi Gayo 250g" in response.data


def test_safety_warning_is_present_on_shop_and_account_pages(client):
    assert b"aplikasi sengaja rentan" in client.get("/").data.lower()
    client.post("/login", data={"username": "budi", "password": "budi123"})
    assert b"aplikasi sengaja rentan" in client.get("/me").data.lower()
