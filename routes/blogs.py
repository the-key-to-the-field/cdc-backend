from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from db.mongo_client import get_db
from bson import ObjectId
from models.blog import blog_schema, blogs_schema

blogs_bp = Blueprint('blogs', __name__)
db = get_db()
blogs_collection = db.get_collection('blogs')

@blogs_bp.route("/blogs", methods=["POST"])
@jwt_required()
def create_blog():
    data = request.json
    current_user = get_jwt_identity()
    
    # Validate and deserialize input
    data['author'] = current_user
    errors = blog_schema.validate(data)
    if errors:
        return jsonify({"message": "Validation error", "errors": errors}), 400
    
    blog = {
        "title": data['title'],
        "image": data['image'],
        "imageKey": data['imageKey'],
        "content": data['content'],
        "author": current_user,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "status": data.get('status', 'draft')
    }
    
    result = blogs_collection.insert_one(blog)
    created_blog = blogs_collection.find_one({"_id": result.inserted_id})
    return jsonify(blog_schema.dump(created_blog)), 201

@blogs_bp.route("/blogs/all", methods=["GET"])
def get_all_blogs():
    blogs = blogs_collection.find().sort("created_at", -1)
    return jsonify(blogs_schema.dump(blogs)), 200

@blogs_bp.route("/blogs", methods=["GET"])
def get_blogs():
    status = request.args.get('status', 'published')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = {"status": status}
    
    total = blogs_collection.count_documents(query)
    blogs = blogs_collection.find(query)\
        .sort("created_at", -1)\
        .skip((page - 1) * per_page)\
        .limit(per_page)
    
    return jsonify({
        "blogs": blogs_schema.dump(blogs),
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }), 200

@blogs_bp.route("/blogs/<blog_id>", methods=["GET"])
def get_blog(blog_id):
    try:
        blog = blogs_collection.find_one({"_id": ObjectId(blog_id)})
        
        if not blog:
            return jsonify({"message": "Blog not found"}), 404
        return jsonify(blog_schema.dump(blog)), 200
    except Exception as e:
        return jsonify({"message": "Invalid blog ID"}), 400
    
@blogs_bp.route("/blogs/<blog_name>/name", methods=["GET"])
def get_blog_by_name(blog_name):
    name = blog_name.replace("-", " ")
    blog = blogs_collection.find_one({"title": name})
    if not blog:
        return jsonify({"message": "Blog not found"}), 404
    return jsonify(blog_schema.dump(blog)), 200 


@blogs_bp.route("/blogs/<blog_id>", methods=["PUT"])
@jwt_required()
def update_blog(blog_id):
    try:
        current_user = get_jwt_identity()
        data = request.json
        
        blog = blogs_collection.find_one({"_id": ObjectId(blog_id)})
        if not blog:
            return jsonify({"message": "Blog not found"}), 404
        
        if blog['author'] != current_user:
            return jsonify({"message": "Unauthorized to update this blog"}), 403
        
        # Validate update data
        update_data = {
            "title": data.get('title', blog['title']),
            "content": data.get('content', blog['content']),
            "image": data.get('image', blog['image']),
            "imageKey": data.get('imageKey', blog['imageKey']),
            "status": data.get('status', blog['status']) if data.get('status') else 'draft',
            "author": current_user,  # needed for validation
            "updated_at": datetime.utcnow()
        }
        
        errors = blog_schema.validate(update_data)
        if errors:
            return jsonify({"message": "Validation error", "errors": errors}), 400
        
        blogs_collection.update_one(
            {"_id": ObjectId(blog_id)},
            {"$set": update_data}
        )
        
        updated_blog = blogs_collection.find_one({"_id": ObjectId(blog_id)})
        return jsonify(blog_schema.dump(updated_blog)), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@blogs_bp.route("/blogs/<blog_id>", methods=["DELETE"])
@jwt_required()
def delete_blog(blog_id):
    try:
        current_user = get_jwt_identity()
        blog = blogs_collection.find_one({"_id": ObjectId(blog_id)})
        
        if not blog:
            return jsonify({"message": "Blog not found"}), 404
        
        if blog['author'] != current_user:
            return jsonify({"message": "Unauthorized to delete this blog"}), 403
        
        blogs_collection.delete_one({"_id": ObjectId(blog_id)})
        return jsonify({"message": "Blog deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@blogs_bp.route("/blogs/user", methods=["GET"])
@jwt_required()
def get_user_blogs():
    current_user = get_jwt_identity()
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = {"author": current_user}
    if status:
        query["status"] = status
    
    total = blogs_collection.count_documents(query)
    blogs = blogs_collection.find(query)\
        .sort("created_at", -1)\
        .skip((page - 1) * per_page)\
        .limit(per_page)
    
    blog_list = []
    for blog in blogs:
        blog['_id'] = str(blog['_id'])
        blog_list.append(blog)
    
    return jsonify({
        "blogs": blog_list,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }), 200

@blogs_bp.route("/blogs/filter", methods=["POST"])
def filter_blogs():
    data = request.json
    page = int(data.get('page', 1))
    per_page = int(data.get('per_page', 10))
    keyword = data.get('keyword', '')
    
    query = {}
    if keyword:
        query["$or"] = [
            {"title": {"$regex": keyword, "$options": "i"}},
            {"content": {"$regex": keyword, "$options": "i"}}
        ]
    
    total = blogs_collection.count_documents(query)
    blogs = blogs_collection.find(query)\
        .sort("created_at", -1)\
        .skip((page - 1) * per_page)\
        .limit(per_page)
    
    return jsonify({
        "items": blogs_schema.dump(blogs),
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page
    }), 200 