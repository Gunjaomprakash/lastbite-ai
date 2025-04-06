# app/routes/barcode.py

import os
import uuid
import requests
import pandas as pd
from datetime import datetime, timedelta
from flask import Blueprint, current_app, request, jsonify, abort

bp = Blueprint('barcode', __name__)

# ── tweak these for your project ────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PRODUCTS_CSV = os.path.join(PROJECT_ROOT, 'data', 'products_table_v2.csv')
LINKS_CSV    = os.path.join(PROJECT_ROOT, 'data', 'user_product_link_table_v2.csv')
DEFAULT_SHELF_LIFE = {
    "Dairy": 7, "Meat": 3, "Produce": 5, "Bakery": 2,
    "Frozen": 180, "Canned Goods": 365, "Snacks": 120, "Beverages": 90,
}
# ----------------------------------------------------------------

def load_products_df():
    if os.path.exists(PRODUCTS_CSV):
        return pd.read_csv(PRODUCTS_CSV, dtype=str)
    return pd.DataFrame(columns=["barcode","name","category","expiry_date"])

def load_links_df():
    if os.path.exists(LINKS_CSV):
        return pd.read_csv(LINKS_CSV, dtype=str)
    return pd.DataFrame(columns=["user_id","product_id","scan_date","quantity"])
@bp.route('/barcode/scan', methods=['POST'])
def scan_barcode():
    data = request.get_json(silent=True) or {}
    barcode = str(data.get('barcode','')).strip()
    if not barcode:
        return jsonify({'error':'barcode required'}), 400

    today = datetime.today().strftime("%Y-%m-%d")
    df = load_products_df()  # reads products_table_v2.csv

    # 1) If already in catalog, return it immediately
    existing = df[df['barcode'] == barcode]
    if not existing.empty:
        row = existing.iloc[0]
        return jsonify({
            'barcode':      barcode,
            'item_name':    row['item_name'],
            'category':     row['category'],
            'expiry_date':  row['expiry_date'],
            'scan_date':    today,
            'already_exists': True
        }), 200

    # 2) Fetch name from OpenFoodFacts
    name = None
    try:
        r = requests.get(
            f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json",
            timeout=5
        )
        j = r.json()
        if j.get('status') == 1:
            name = j['product'].get('product_name')
    except Exception as e:
        current_app.logger.warning(f"OFF error: {e}")
    if not name:
        name = "Unknown product"

    # 3) Prepare categories list
    existing_cats = sorted(df['category'].dropna().unique().tolist())
    all_cats = sorted(set(existing_cats) | set(DEFAULT_SHELF_LIFE.keys()))

    # 4) Suggest expiry based on first default category
    default_cat = all_cats[0] if all_cats else 'Misc'
    days = DEFAULT_SHELF_LIFE.get(default_cat, 30)
    suggested = (datetime.today() + timedelta(days=days)).strftime("%Y-%m-%d")

    return jsonify({
        'barcode':         barcode,
        'item_name':       name,
        'categories':      all_cats,
        'suggested_expiry': suggested,
        'scan_date':       today,
        'already_exists':  False
    }), 200

@bp.route('/barcode/confirm', methods=['POST'])
def confirm_barcode():
    data     = request.get_json(silent=True) or {}
    barcode  = str(data.get('barcode','')).strip()
    category = str(data.get('category','')).strip()
    user_id  = str(data.get('user_id','')).strip()
    item_name= data.get('item_name','Unknown product')
    if not all([barcode, category, user_id]):
        return jsonify({'error':'barcode, category & user_id required'}), 400

    today = datetime.today().strftime("%Y-%m-%d")
    df   = load_products_df()

    # 1) Append to products if missing
    if df[df['barcode'] == barcode].empty:
        # new product_uid
        uid = str(uuid.uuid4())
        # default expiry
        days = DEFAULT_SHELF_LIFE.get(category, 30)
        expiry = (datetime.today() + timedelta(days=days)).strftime("%Y-%m-%d")

        df = df.append({
            'product_uid': uid,
            'product_id':  uid,
            'barcode':     barcode,
            'item_name':   item_name,
            'category':    category,
            'scanned_date': today,
            'expiry_date': expiry
        }, ignore_index=True)

        try:
            df.to_csv(PRODUCTS_CSV, index=False)
        except Exception as e:
            current_app.logger.error(f"Saving products CSV failed: {e}")
            abort(500, 'could not save product catalog')
    else:
        # existing uid & expiry
        row = df[df['barcode'] == barcode].iloc[0]
        uid = row['product_uid']
        expiry = row['expiry_date']

    # 2) Append to user–product links
    links = load_links_df()
    links = links.append({
        'user_id':     user_id,
        'product_id':  uid,
        'scan_date':   today,
        'quantity':    data.get('quantity', 1)
    }, ignore_index=True)
    try:
        links.to_csv(LINKS_CSV, index=False)
    except Exception as e:
        current_app.logger.error(f"Saving links CSV failed: {e}")
        abort(500, 'could not save user link')

    # 3) Return the full record
    return jsonify({
        'uid':         uid,
        'barcode':     barcode,
        'item_name':   item_name,
        'category':    category,
        'expiry_date': expiry,
        'scan_date':   today,
        'quantity':    data.get('quantity', 1)
    }), 201