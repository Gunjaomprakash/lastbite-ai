# app/routes/confirm_product.py

import os
import uuid
import pandas as pd
from flask import Blueprint, request, jsonify, current_app, abort

bp = Blueprint('confirm_product', __name__)

# ── tweak these paths to match your setup ─────────────────────────
BASE_DIR                = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
USER_PRODUCT_LINK_PATH  = os.path.join(BASE_DIR, 'data', 'user_product_link_table_v2.csv')
USERS_DB_PATH           = os.path.join(BASE_DIR, 'data', 'users_table_v2.csv')
PRODUCTS_DB_PATH        = os.path.join(BASE_DIR, 'data', 'products_table_v2.csv')
# ------------------------------------------------------------------

# In‑memory cache
_user_product_df = None
_users_df        = None
_products_df     = None

def get_user_product_df():
    global _user_product_df
    if _user_product_df is None:
        if os.path.exists(USER_PRODUCT_LINK_PATH):
            _user_product_df = pd.read_csv(USER_PRODUCT_LINK_PATH, dtype=str)
        else:
            _user_product_df = pd.DataFrame(columns=['user_uid','product_uid','scan_date','quantity'])
    return _user_product_df

def get_users_df():
    global _users_df
    if _users_df is None:
        if os.path.exists(USERS_DB_PATH):
            _users_df = pd.read_csv(USERS_DB_PATH, dtype=str)
        else:
            _users_df = pd.DataFrame(columns=['user_uid','user_id','user_name','location_lat','location_lng','points_awarded'])
    return _users_df

def get_products_df():
    global _products_df
    if _products_df is None:
        if os.path.exists(PRODUCTS_DB_PATH):
            _products_df = pd.read_csv(PRODUCTS_DB_PATH, dtype=str)
        else:
            _products_df = pd.DataFrame(columns=['product_uid','product_id','barcode','item_name','category','scanned_date','expiry_date'])
    return _products_df

def save_user_product_link(df: pd.DataFrame):
    try:
        df.to_csv(USER_PRODUCT_LINK_PATH, index=False)
    except Exception as e:
        current_app.logger.error(f"Failed to save user-product links: {e}")
        abort(500, "could not save link data")

@bp.route('/confirm-product', methods=['POST'])
def confirm_product():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    user_uid    = data.get('user_uid')
    product_uid = data.get('product_uid')
    scan_date   = data.get('scan_date') or pd.Timestamp.today().strftime('%Y-%m-%d')
    quantity    = str(data.get('quantity', '1'))

    # Validate inputs
    if not user_uid or not product_uid:
        return jsonify({"error": "Missing user_uid or product_uid"}), 400

    users_df    = get_users_df()
    products_df = get_products_df()

    if user_uid not in users_df['user_uid'].values:
        return jsonify({"error": f"User {user_uid} not found"}), 404

    if product_uid not in products_df['product_uid'].values:
        return jsonify({"error": f"Product {product_uid} not found"}), 404

    # Load existing links
    links_df = get_user_product_df()

    # Check for existing link
    exists = links_df[
        (links_df['user_uid'] == user_uid) &
        (links_df['product_uid'] == product_uid)
    ]
    if not exists.empty:
        return jsonify({
            "message": "Link already exists",
            "status": "unchanged"
        }), 200

    # Append new link
    new_link = {
        'user_uid': user_uid,
        'product_uid': product_uid,
        'scan_date': scan_date,
        'quantity': quantity
    }
    links_df = pd.concat([links_df, pd.DataFrame([new_link])], ignore_index=True)

    # Save back to CSV
    save_user_product_link(links_df)
    # Update in‑memory cache
    global _user_product_df
    _user_product_df = links_df

    return jsonify({
        "message": "Product confirmed and linked to user",
        "user_uid": user_uid,
        "product_uid": product_uid,
        "scan_date": scan_date,
        "quantity": quantity,
        "status": "created"
    }), 201