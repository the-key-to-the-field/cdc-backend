from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required
from db.mongo_client import get_db
from marshmallow import ValidationError
from models.product import product_schema
from datetime import datetime

# Initialize the blueprint
products_bp = Blueprint('products', __name__)

# Get the database connection
db = get_db()
products_collection = db.get_collection('products')
categories_collection = db.get_collection('categories')

@products_bp.route("/products", methods=["POST"])
@jwt_required()
def create_product():
    try:
        data = product_schema.load(request.json)
        data["price"] = float(data["price"] or 0)
        data["categoryId"] = ObjectId(data["categoryId"])
        data["createdAt"] = datetime.now()
        data["updatedAt"] = datetime.now()
    except ValidationError as err:
        return jsonify(err.messages), 400

    result = products_collection.insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201


@products_bp.route("/products", methods=["GET"])
def get_products():
    products = list(products_collection.find())
    for product in products:
        product["_id"] = str(product["_id"])
        # Ensure images is a list
        product["images"] = product.get("images", [])
    return jsonify(products), 200

@products_bp.route("/products/filter", methods=["POST"])
# @jwt_required()
def get_productsFiltered():
    try:
        data = request.json
        # Validate input data
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid input format, expected JSON object"}), 422
        
        page = data.get('page', 1)
        limit = data.get('limit', 10)
        keyword = data.get('keyword', '')

        # Ensure page and limit are integers
        try:
            page = int(page)
            limit = int(limit)
        except ValueError:
            return jsonify({"error": "Page and limit must be integers"}), 422

        # Calculate the offset
        skip = (page - 1) * limit
        
        # Fetch the products with pagination and sort by recent
        products = list(products_collection.find(
            {"name": {"$regex": keyword, "$options": "i"}}
        ).sort("createdAt", -1).skip(skip).limit(limit))
        
        for product in products:
            product["_id"] = str(product["_id"])
            # Convert string ID back to ObjectId for lookup
            category = categories_collection.find_one({"_id": product["categoryId"]}) if "categoryId" in product else None
            product["categoryId"] = str(product["categoryId"]) if "categoryId" in product else ""
            product["categoryName"] = category["name"] if category else ""

        # Get the total count of products matching the keyword
        total_products = products_collection.count_documents(
            {"name": {"$regex": keyword, "$options": "i"}}
        )
        
        return jsonify({
            "items": products,
            "total": total_products,
            "page": page,
            "pages": (total_products + limit - 1) // limit
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@products_bp.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    product = products_collection.find_one({"_id": ObjectId(product_id)})
    if product:
        product["_id"] = str(product["_id"])
        product["images"] = product.get("images", [])  # Ensure images is a list
        category = categories_collection.find_one({"_id": product["categoryId"]}) if "categoryId" in product else None
        product["categoryName"] = category["name"] if category else ""
        product["categoryId"] = str(product["categoryId"])

        return jsonify(product), 200
    return jsonify({"error": "Product not found"}), 404

@products_bp.route("/products/<product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    try:
        data = product_schema.load(request.json)
        data["price"] = float(data["price"] or 0)
        data["categoryId"] = ObjectId(data["categoryId"]) if "categoryId" in data else None
        data["updatedAt"] = datetime.now()
    except ValidationError as err:
        return jsonify(err.messages), 400

    result = products_collection.update_one({"_id": ObjectId(product_id)}, {"$set": data})
    if result.matched_count:
        return jsonify({"message": "Product updated"}), 200
    return jsonify({"error": "Product not found"}), 404

@products_bp.route("/products/<product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    result = products_collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count:
        return jsonify({"message": "Product deleted"}), 200
    return jsonify({"error": "Product not found"}), 404

@products_bp.route("/products/category/<category_id>", methods=["GET"])
def get_products_by_category(category_id):
    try:
        products = list(products_collection.find({"categoryId": ObjectId(category_id)}))
        for product in products:
            product["_id"] = str(product["_id"])
            category = categories_collection.find_one({"_id": product["categoryId"]}) if "categoryId" in product else None
            product["categoryId"] = str(product["categoryId"])
            product["categoryName"] = category["name"] if category else ""
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
    
    # Get all products by category name
@products_bp.route('/products/category/<category_name>/name', methods=['GET'])
def get_products_by_category_name(category_name):
        name = category_name.lower()
        products = list(products_collection.find())
        for product in products:
            product["_id"] = str(product["_id"])
            category = categories_collection.find_one({"_id": product["categoryId"]}) if "categoryId" in product else None
            product["categoryId"] = str(product["categoryId"])
            product["categoryName"] = category["name"].lower() if category else ""  
        products = [product for product in products if product["categoryName"] == name]
        
        return jsonify(products), 200

@products_bp.route('/products/ids', methods=['GET'])
def get_all_products_ids():
    products = products_collection.find({}, {'_id': 1})
    product_ids = [str(product['_id']) for product in products]
    return jsonify(product_ids)


@products_bp.route('/update-product-fields', methods=['POST'])
def update_product_fields():
    try:
        # Get all products
        products = products_collection.find()
        
        # Counter for updated records
        updated_count = 0
        
        # Process each product
        for product in products:
            update_data = {}
            
            # Check and update image field
            if 'image' in product and 'images' not in product:
                update_data['images'] = [product['image']]
                update_data['image'] = None  # To unset the old field
            
            # Check and update imageKey field
            if 'imageKey' in product and 'imageKeys' not in product:
                update_data['imageKeys'] = [product['imageKey']]
                update_data['imageKey'] = None  # To unset the old field
            
            # If we have updates to make
            if update_data:
                # Use $set and $unset operators for MongoDB
                update_query = {}
                if 'images' in update_data or 'imageKeys' in update_data:
                    update_query['$set'] = {
                        k: v for k, v in update_data.items() 
                        if k in ['images', 'imageKeys']
                    }
                if None in update_data.values():
                    update_query['$unset'] = {
                        k: "" for k, v in update_data.items() 
                        if v is None
                    }
                
                result = products_collection.update_one(
                    {"_id": product["_id"]},
                    update_query
                )
                if result.modified_count:
                    updated_count += 1
        
        return jsonify({
            'status': 'success',
            'message': f'Updated {updated_count} products successfully',
            'updated_count': updated_count
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error updating products: {str(e)}'
        }), 500