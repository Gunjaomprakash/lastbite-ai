# app/routes/inventory.py

import os
import csv
from flask import Blueprint, current_app, jsonify, abort

bp = Blueprint('inventory', __name__)

# PROJECT_ROOT/backend/app/routes -> go up 3 levels to backend/, then into data/
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')
)
DATA_DIR      = os.path.join(PROJECT_ROOT, 'data')
LINK_FILE     = os.path.join(DATA_DIR, 'user_product_link_table_v2.csv')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products_table_v2.csv')

@bp.route('/inventory/<user_uid>', methods=['GET'])
def get_inventory(user_uid):
    # Load user–product links for this user
    links = []
    try:
        with open(LINK_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('user_uid') == user_uid:
                    links.append({
                        'product_uid': row['product_uid'],
                        'quantity': int(row.get('quantity', 0))
                    })
    except Exception as e:
        current_app.logger.error(f"Error reading {LINK_FILE}: {e}")
        abort(500, 'could not read link data')

    # Load product details
    products = {}
    try:
        with open(PRODUCTS_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products[row['product_uid']] = row
    except Exception as e:
        current_app.logger.error(f"Error reading {PRODUCTS_FILE}: {e}")
        abort(500, 'could not read product data')

    # Build joined inventory
    inventory = []
    for link in links:
        prod = products.get(link['product_uid'])
        if prod:
            item = {**prod, 'quantity': link['quantity']}
            inventory.append(item)
        else:
            current_app.logger.warning(f"Missing product {link['product_uid']}")

    return jsonify({'user_uid': user_uid, 'inventory': inventory})