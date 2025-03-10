import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from routes.products import products_bp
from routes.users import users_bp
from routes.blogs import blogs_bp
from routes.categories import categories_bp
from db.mongo_client import get_db
from waitress import serve
from datetime import timedelta

app = Flask(__name__)
# CORS(app, supports_credentials=True, resources={
#     r"/api/*": {
#         "origins": ["http://localhost:3000"],  # Replace with your frontend URL
#         "methods": ["GET", "POST", "PUT", "DELETE"],
#         "allow_headers": ["Content-Type", "Authorization"],
#         "Access-Control-Allow-Credentials": True,
#         'Access-Control-Allow-Origin': '*'
#     }
# })
CORS(app, supports_credentials=True)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)

# Initialize the database connection
db = get_db()

app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(blogs_bp, url_prefix='/api')
app.register_blueprint(categories_bp, url_prefix='/api')

if __name__ == "__main__":  
    serve(app, host='127.0.0.0', port=5000) 