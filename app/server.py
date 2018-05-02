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
from flasgger import Swagger
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

# Configure Swagger before initilaizing it
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "specs": [
        {
            "version": "1.0.0",
            "title": "DevOps Swagger Products App",
            "description": "This is a sample server Products server.",
            "endpoint": 'v1_spec',
            "route": '/v1/spec'
        }
    ]
}

# Initialize Swagger after configuring it
Swagger(app)

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
    """ Removes a Product from the database that matches the id
    This endpoint will delete a Product based the id specified in the path
    ---
    tags:
      - Products
    description: Deletes a Product from the database
    parameters:
      - name: id
        in: path
        description: ID of product to delete
        type: integer
        required: true
    responses:
      204:
        description: Product deleted
    """
    Product.catalog.delete(id)

    return make_response('', HTTP_204_NO_CONTENT)


######################################################################
# LIST PRODUCTS
######################################################################
@app.route('/products', methods=['GET'])
def list_products():
    """ 
    Retrieves a list of products from the database
    This endpoint will return all Pets unless a query parameter is specificed
    ---
    tags:
      - Products
    description: The Products endpoint allows you to query Products
    parameters:
      - name: category
        in: query
        description: the category of Product you are looking for
        required: false
        type: string
      - name: name
        in: query
        description: the name of Product you are looking for
        required: false
        type: string
    definitions:
      Product:
        type: object
        properties:
          id:
            type: integer
            description: unique id assigned internallt by service
          name:
            type: string
            description: the products's name
          category:
            type: string
            description: the category of product (e.g., iphone, tc, etc.)
    responses:
      200:
        description: An array of Products
        schema:
          type: array
          items:
            schema:
              $ref: '#/definitions/Product'
    """
    results = []
    keyword = request.args.get('keyword')
    if keyword:
        results = Product.catalog.query(keyword)
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
    """ Retrieves a Product with a specific id
    This endpoint will return a Product based on it's id
    ---
    tags:
      - Products
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of product to retrieve
        type: integer
        required: true
    responses:
      200:
        description: Product returned
        schema:
          $ref: '#/definitions/Product'
      404:
        description: Product not found
    """
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
    """ Creates a product and saves it
    This endpoint will create a Product based the data in the body that is posted
    ---
    tags:
      - Products
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - name
            - price
            - id
            - image_id
            - description
            - review_list
          properties:
            name:
              type: string
              description: name for the product
            price:
              type: string
              description: the price of product
            id:
              type: integer
              description: id for the product
            image_id:
              type: integer
              description: image id for the product
            description:
              type: string
              description: description for the product
            review_list:
              type: array
              items:
                type: object
                properties:
                  username:
                    type: string
                    description: username for the reviewer
                  score:
                    type: integer
                    description: score the product receive
                  date:
                    type: string
                    description: time that product receive review
                  detail:
                    type: string
                    description: review detail description
    responses:
      201:
        description: Product created
        schema:
          $ref: '#/definitions/Product'
      400:
        description: Bad Request (the posted data was not valid)
    """
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
    """ Updates a product in the catalog
    This endpoint will update a Product based the body that is posted
    ---
    tags:
      - Products
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of product to retrieve
        type: integer
        required: true
      - in: body
        name: body
        schema:
          id: data
          required:
            - name
            - category
          properties:
            name:
              type: string
              description: name for the Product
            category:
              type: string
              description: the category of product (iphone, macbook, etc.)
    responses:
      200:
        description: Pet Updated
        schema:
          $ref: '#/definitions/Product'
      400:
        description: Bad Request (the posted data was not valid)
    """
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
