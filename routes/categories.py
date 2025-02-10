from flask import Blueprint, request, jsonify
from models.category import Category
from db.mongo_client import get_db
from bson import ObjectId
from datetime import datetime
from flask_jwt_extended import jwt_required

categories_bp = Blueprint('categories', __name__)
db = get_db()
categories_collection = db.get_collection('categories')
products_collection = db.get_collection('products')

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = categories_collection.find()
    return jsonify([{
        'id': str(c['_id']),
        'name': c['name'],
        'image': c['image'] if 'image' in c else None,
        # 'imageKey': c['imageKey'] if 'imageKey' in c else None,
    } for c in categories])

@categories_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    category = Category(name=data['name'], image=data['image'], imageKey=data['imageKey'])
    result = categories_collection.insert_one(category.to_dict())
    return jsonify({'id': str(result.inserted_id), 'name': data['name']}), 201

@categories_bp.route('/categories/<id>', methods=['PUT'])
def update_category(id):
    data = request.get_json()
    categories_collection.update_one(
        {'_id': ObjectId(id)},
        {'$set': {
            'name': data.get('name'),
            'image': data.get('image'),
            'imageKey': data.get('imageKey'),
            'updated_at': datetime.utcnow()
        }}
    )
    return jsonify({'id': id, 'name': data.get('name')})

@categories_bp.route('/categories/<id>', methods=['DELETE'])
@jwt_required()
def delete_category(id):
    categories_collection.delete_one({'_id': ObjectId(id)})
    products_collection.update_many(
        {'categoryId': ObjectId(id)},
        {'$set': {'categoryId': None, 'categoryName': None}}
    )   
    return jsonify({'message': 'Category deleted successfully'}), 200

@categories_bp.route('/categories/<id>', methods=['GET'])
def get_category(id):
    category = categories_collection.find_one({'_id': ObjectId(id)})
    if not category:
        return jsonify({'message': 'Category not found'}), 404
    return jsonify({
        'id': str(category['_id']),
        'name': category['name'],
        'image': category['image'] if 'image' in category else None,
        'imageKey': category['imageKey'] if 'imageKey' in category else None,
    })

@categories_bp.route('/categories/filter', methods=['POST'])
def filter_categories():
    data = request.get_json()
    page = int(data.get('page', 1))
    per_page = int(data.get('per_page', 10))
    keyword = data.get('keyword', '')
    
    query = {}

    if keyword:
        query['name'] = {'$regex': keyword, '$options': 'i'}

    total = categories_collection.count_documents(query)
    pages = (total + per_page - 1) // per_page

    categories = categories_collection.find(query).skip((page - 1) * per_page).limit(per_page)
    
    return jsonify({
        'items': [{
            'id': str(c['_id']),
            'name': c['name'],
            'image': c['image'] if 'image' in c else None,
            'imageKey': c['imageKey'] if 'imageKey' in c else None,
            'created_at': c['created_at'],
            'updated_at': c['updated_at']
        } for c in categories],
        'page': page,
        'pages': pages,
        'total': total
    }) 