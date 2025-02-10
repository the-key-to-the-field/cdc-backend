# This file can be empty 
from flask import Blueprint

def create_blueprint(name):
    return Blueprint(name, __name__)

products_bp = create_blueprint("products")
users_bp = create_blueprint("users")
blogs_bp = create_blueprint("blogs")

