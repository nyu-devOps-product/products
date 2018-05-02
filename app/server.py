"""
This service is written with Python Flask
Paths
-----
GET   /products - Retrieves a list of product from the database
GET   /products/{id} - Retrirves a product with a specific id
POST  /products - Creates a product in the datbase from the posted database
PUT   /products/{id} - Updates a product in the database fom the posted database
DELETE /products/{id} - Removes a product from the database that matches the id
"""

import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from app.models import Product, DataValidationError, Review
from . import app
# Pull options from environment
# DEBUG = (os.getenv('DEBUG', 'False') == 'True')
# PORT = os.getenv('PORT', '5000')

# Create Flask application
# app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409


######################################################################
# Error Handlers
######################################################################
import error_handlers

######################################################################
# GET HEALTH CHECK
######################################################################


@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)

######################################################################
# GET INDEX
######################################################################


@app.route('/')
def index():
    # data = '{name: <string>, category: <string>}'
    # url = request.base_url + 'pets' # url_for('list_pets')
    # return jsonify(name='Pet Demo REST API Service', version='1.0', url=url,
    # data=data), status.HTTP_200_OK
    return app.send_static_file('index.html')


######################################################################
# DELETE A PRODUCT
######################################################################
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_products(id):
    """ Removes a Product from the database that matches the id """
    Product.catalog.delete(id)

    return make_response('', HTTP_204_NO_CONTENT)


######################################################################
# LIST PRODUCTS
######################################################################
@app.route('/products', methods=['GET'])
def list_products():
    """ Retrieves a list of products from the database """
    results = []
    if request.args:
        temp = Product.catalog.all()
        for keyword in request.args:
            if keyword != 'sort':
                temp = list(set(temp) & set(
                    Product.catalog.query(keyword, request.args[keyword])))
        results = temp
    else:
        results = Product.catalog.all()
    products = results
    sort_type = request.args.get('sort')
    if sort_type == 'price':
        # Retrieves a list of products with the lowest price showed first from
        # the database
        results = sorted(products, key=lambda p: float(
            p.get_price()), reverse=False)
    elif sort_type == 'price-':
        # Retrieves a list of products with the highest price showed first from
        # the database
        results = sorted(products, key=lambda p: float(
            p.get_price()), reverse=True)
    elif sort_type == 'review':
        # Retrieves a list of products with the highest review showed first
        # from the database
        results = sorted(products, key=lambda p: p.avg_score(), reverse=True)
    elif sort_type == 'name':
        # Retrieves a list of products in alphabetical order from the database
        results = sorted(
            products, key=lambda p: p.get_name().lower(), reverse=False)
    elif sort_type == 'name-':
        # Retrieves a list of products in reverse alphabetical order from the
        # database
        results = sorted(
            products, key=lambda p: p.get_name().lower(), reverse=True)
#    else:
#        results = Product.catalog.all()

    return jsonify([product.serialize() for product in results]), HTTP_200_OK


######################################################################
# RETRIEVE A PRODUCT BY ID
######################################################################
@app.route('/products/<int:id>', methods=['GET'])
def get_products(id):
    """ Retrieves a Product with a specific id """
    product = Product.catalog.find(id)
    if product:
        message = product.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error': 'product with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code


######################################################################
# ADD A NEW PRODUCT
######################################################################
@app.route('/products', methods=['POST'])
def create_product():
    """ Creates a product and saves it """
    payload = request.get_json()
    # Ensure that required attributes are provided:
    if ('name' not in payload or 'price' not in payload):
        abort(400)
    # Pass on all parameters specified to new product:
    product = Product(**payload)
    product.deserialize(payload)
    product.catalog.save(product)
    message = product.serialize()
    response = make_response(jsonify(message), HTTP_201_CREATED)
    response.headers['Location'] = url_for(
        'get_products', id=product.id, _external=True)
    return response


######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route('/products/<int:id>', methods=['PUT'])
def update_products(id):
    """ Updates a product in the catalog """
    product = Product.catalog.find(id)
    if product:
        payload = request.get_json()
        if ('name' not in payload or 'price' not in payload):
            abort(400)
        product.deserialize(payload)
        product.catalog.save(product)
        message = product.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Product with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code


######################################################################
# ACTION ON AN EXISTING PRODUCT: ADD REVIEW
######################################################################
@app.route('/products/<int:id>/review', methods=['PUT'])
def review_products(id):
    """ Adds a review to product in the catalog """
    product = Product.catalog.find(id)
    if product:
        payload = request.get_json()
        # Ensure that required attributes are provided:
        if ('username' not in payload or 'score' not in payload):
            abort(400)
        # Pass on new review to product:
        review = Review(**payload)
        review_list = product.get_review_list()
        review_list.append(review)
        product.set_review_list(review_list)
        product.catalog.save(product)
        message = product.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Product with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code


######################################################################
#   U T I L I T Y   F U N C T I O N S
######################################################################
def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')


######################################################################
#   M A I N
######################################################################
# if __name__ == "__main__":
#     print "*********************************"
#     print " P R O D U C T   S H O P   S E R V I C E "
#     print "*********************************"
#     initialize_logging()
#     phone_review_list = [Review(username="applefan", score="4", detail="OK"),
#                          Review(username="helloworld",
#                                 score="4", detail="As expected"),
#                          Review(username="pythonfan", score="3", detail="So So")]
#     pc_review_list = [Review(username="applelover", score="5", detail="Excellent"),
#                       Review(username="tvfan", score="5",
#                              detail="Loving this!!"),
#                       Review(username="devops team member",
#                              score="5", detail="Highly recommend!"),
#                       Review(username="nyu", score="5", detail="Nice!")]
#     Product.catalog.save(
#         Product("iPhone 8", 649, 0, review_list=phone_review_list))
#     Product.catalog.save(
#         Product("MacBook Pro", 1799, 1, review_list=pc_review_list))
#     app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
