# Flask Blog API

A RESTful API built with Flask for managing blog posts, products and categories.

## Features

- User authentication with JWT
- CRUD operations for blog posts
- CRUD operations for products and categories
- Image upload support
- Pagination and filtering
- MongoDB database

## API Endpoints

### Blogs

- `POST /blogs` - Create a new blog post
- `GET /blogs` - Get all published blog posts
- `GET /blogs/<id>` - Get a specific blog post
- `PUT /blogs/<id>` - Update a blog post
- `DELETE /blogs/<id>` - Delete a blog post
- `GET /blogs/user` - Get current user's blog posts
- `POST /blogs/filter` - Filter blog posts

### Products

- `POST /products` - Create a new product
- `GET /products` - Get all products
- `GET /products/<id>` - Get a specific product
- `PUT /products/<id>` - Update a product
- `DELETE /products/<id>` - Delete a product
- `GET /products/category/<id>` - Get products by category
- `POST /products/filter` - Filter products

## Setup

1. Clone the repository
2. Create and activate virtual environment:
