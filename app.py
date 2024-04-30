from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://gnusacls:7-fq3YkDvcc7GxkcrUu_H6kc5hewXTsJ@lucky.db.elephantsql.com/gnusacls"
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate
CORS(app)

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    img_url = db.Column(db.String(400), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Categories', backref=db.backref('products', lazy=True))

# Initialize Marshmallow

class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Categories
        sqla_session = db.session

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products
        sqla_session = db.session
        include_fk = True  # Include foreign keys

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

with app.app_context():
    db.create_all()

@app.route('/category', methods=['POST'])
def create_category():
    name = request.json['name']
    new_category = Categories(name=name)
    db.session.add(new_category)
    db.session.commit()
    return category_schema.dump(new_category)

## get all categories
@app.route('/category', methods=['GET'])
def get_categories():
    categories = Categories.query.all()
    return {'categories': categories_schema.dump(categories)}

@app.route('/product', methods=['POST'])
def create_product():
    name = request.json['name']
    price = request.json['price']
    img_url = request.json['img_url']
    category_id = request.json['category_id']
    new_product = Products(name=name, price=price, img_url=img_url, category_id=category_id)
    db.session.add(new_product)
    db.session.commit()
    return product_schema.dump(new_product)

# get procucts by category
@app.route('/product/<category_id>', methods=['GET'])
def get_products(category_id):
    products = Products.query.filter_by(category_id=category_id).all()
    return {'products': products_schema.dump(products)}

# get last 16 products
@app.route('/product', methods=['GET'])
def get_last_products():
    products = Products.query.order_by(Products.id.desc()).limit(16).all()
    return {'products': products_schema.dump(products)}

# search product with query string
@app.route('/product/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    products = Products.query.filter(Products.name.ilike(f'%{query}%')).all()
    return {'products': products_schema.dump(products)}

# get product by id
@app.route('/product/id/<product_id>', methods=['GET'])
def get_product(product_id):
    product = Products.query.get(product_id)
    return product_schema.dump(product)

if __name__ == '__main__':
    app.run()
    app.run(debug=True)