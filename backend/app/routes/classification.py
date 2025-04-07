from flask import Blueprint, request, jsonify, send_file
from app.services.classification_service import predict_fruit_state
import numpy as np
from PIL import Image
import io
import os
import openai
import base64
import json
import re
import pandas as pd
from datetime import datetime, timedelta

bp = Blueprint('classification', __name__)

# Load and cache the product database
PRODUCTS_DB_PATH = '/Users/omprakashgunja/Documents/GitHub/lastbite-ai/backend/data/products_table_v2.csv'
products_df = None

def get_products_df():
    """Load products database if not already loaded"""
    global products_df
    if products_df is None:
        products_df = pd.read_csv(PRODUCTS_DB_PATH)
    return products_df

def find_matching_products(item_name, state):
    """Find matching products in the database based on item name"""
    df = get_products_df()
    
    # Case-insensitive match on item_name
    matches = df[df['item_name'].str.lower() == item_name.lower()]
    
    if matches.empty:
        return None
    
    # Get current date
    today = datetime.now().date()
    
    # Get the first matching product
    product = matches.iloc[0].to_dict()
    
    # If item is rotten but has a future expiry date, override it to be expiring soon
    if state.lower() == 'rotten' and 'expiry_date' in product and product['expiry_date']:
        # Store original expiry
        product['original_expiry'] = product['expiry_date']
        
        # Set expiry to yesterday or today
        product['expiry_date'] = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        product['expiry_overridden'] = True
    
    # Calculate days until expiry
    if 'expiry_date' in product and product['expiry_date']:
        try:
            expiry_date = datetime.strptime(product['expiry_date'], '%Y-%m-%d').date()
            product['days_until_expiry'] = (expiry_date - today).days
        except ValueError:
            product['days_until_expiry'] = None
    else:
        product['days_until_expiry'] = None
    
    return product


@bp.route("/classify/model", methods=["POST"])
def classify_with_model():
    """Classify fruit using custom trained model"""
    print("Received request for model classification")
    print(request.files)
    
    # make sure 'image' is in the form data
    if "image" not in request.files:
        return jsonify({"error": "no image uploaded"}), 400

    img = request.files["image"]
    try:
        # Get prediction from our model
        result = predict_fruit_state(img)
        
        # Enrich with database information
        if 'fruit' in result and 'state' in result:
            db_info = find_matching_products(result['fruit'], result['state'])
            if db_info:
                result['product_info'] = db_info
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/classify/openai", methods=["POST"])
def classify_with_openai():
    """Classify fruit using OpenAI vision model"""
    print("Received request for OpenAI classification")
    print(request.files)
    
    # make sure 'image' is in the form data
    if "image" not in request.files:
        return jsonify({"error": "no image uploaded"}), 400

    img = request.files["image"]
    try:
        # Reset file cursor
        img.seek(0)
        
        try:
            # Create OpenAI client
            client = openai.OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
            
            # Read and encode image
            img_data = img.read()
            print(f"Image size: {len(img_data)} bytes")
            encoded_img = base64.b64encode(img_data).decode('utf-8')
            
            # Call OpenAI API
            print("Calling OpenAI API...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Identify this fruit and tell me if it's fresh or rotten. Reply with JSON only: {\"fruit\": \"name\", \"state\": \"fresh or rotten\"}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_img}"}}
                        ]
                    }
                ],
                max_tokens=300
            )
            print("OpenAI API response received")
            
            openai_text = response.choices[0].message.content.strip()
            print(f"OpenAI response: {openai_text}")
            
            json_match = re.search(r'\{.*\}', openai_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                result["source"] = "openai"
                
                # Enrich with database information
                if 'fruit' in result and 'state' in result:
                    db_info = find_matching_products(result['fruit'], result['state'])
                    if db_info:
                        result['product_info'] = db_info
                
                return jsonify(result), 200
            else:
                return jsonify({"error": "OpenAI response format not as expected", "raw_response": openai_text}), 400
        
        except openai.OpenAIError as e:
            print(f"OpenAI API error: {str(e)}")
            return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return jsonify({"error": f"Failed to parse OpenAI response as JSON: {str(e)}"}), 500
        except Exception as e:
            print(f"Unexpected error in OpenAI processing: {str(e)}")
            return jsonify({"error": f"Error processing OpenAI request: {str(e)}"}), 500
                
    except Exception as e:
        print(f"General error in classify_with_openai: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Keep the original combined endpoint for backward compatibility
@bp.route("/classify", methods=["POST"])
def classify():
    """Classify fruit using model with OpenAI fallback"""
    print("Received request for classification with fallback")
    print(request.files)
    
    # make sure 'image' is in the form data
    if "image" not in request.files:
        return jsonify({"error": "no image uploaded"}), 400

    img = request.files["image"]
    try:
        # Get prediction from our model
        result = predict_fruit_state(img)
        
        # Enrich with database information
        if 'fruit' in result and 'state' in result:
            db_info = find_matching_products(result['fruit'], result['state'])
            if db_info:
                result['product_info'] = db_info
        
        # Check if confidence is below threshold
        confidence_threshold = 0.6  # Adjust as needed
        if result.get('confidence', 1.0) < confidence_threshold:
            # Use OpenAI API for a secondary prediction
            
            # Reset file cursor
            img.seek(0)
            
            # Create OpenAI client
            client = openai.OpenAI(api_key= os.getenv("OPENAI_API_KEY"))
            
            # Read and encode image
            img_data = img.read()
            encoded_img = base64.b64encode(img_data).decode('utf-8')
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Identify this fruit and tell me if it's fresh or rotten. Reply with JSON only: {\"fruit\": \"name\", \"state\": \"fresh or rotten\"}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_img}"}}
                        ]
                    }
                ],
                max_tokens=300
            )
            
            try:
                openai_text = response.choices[0].message.content.strip()
                json_match = re.search(r'\{.*\}', openai_text, re.DOTALL)
                if json_match:
                    openai_result = json.loads(json_match.group(0))
                    
                    # Check if OpenAI result differs from our model's prediction
                    new_result = {
                        "fruit": openai_result.get("fruit", result.get("fruit")),
                        "state": openai_result.get("state", result.get("state")),
                        "source": "openai",
                        "original_confidence": result.get("confidence", 0)
                    }
                    
                    # Get new product info if fruit or state changed
                    if (new_result['fruit'] != result.get('fruit') or 
                        new_result['state'] != result.get('state')):
                        db_info = find_matching_products(new_result['fruit'], new_result['state'])
                        if db_info:
                            new_result['product_info'] = db_info
                    elif 'product_info' in result:
                        new_result['product_info'] = result['product_info']
                    
                    result = new_result
                else:
                    result["note"] = "Low confidence, OpenAI response format not as expected"
            except Exception as e:
                result["note"] = f"Low confidence, OpenAI fallback failed: {str(e)}"
                
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500