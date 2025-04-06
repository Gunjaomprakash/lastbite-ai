from flask import Blueprint, request, jsonify, send_file
from app.services.classification_service import predict_fruit_state
import numpy as np
from PIL import Image
import io

bp = Blueprint('classification', __name__)


@bp.route("/classify", methods=["POST"])
def classify():
    print("Received request")
    print(request.files)
    
    # make sure 'image' is in the form data
    if "image" not in request.files:
        return jsonify({"error": "no image uploaded"}), 400

    img = request.files["image"]
    try:
        result = predict_fruit_state(img)
        # result should be a dict, e.g. {"fruit":"apple","state":"fresh"}
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@bp.route('/getimage', methods=['GET'])
def test_image():
    return 'hello'