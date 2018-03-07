import os
import sys
import logging
from functools import wraps

from flask import Flask, Response, jsonify, request, json, url_for, make_response, abort
from models import Product, DataValidationError, Review

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# Create Flask application
app = Flask(__name__)
app.config['LOGGING_LEVEL'] = logging.INFO

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415


######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles all data validation issues from the model """
    return bad_request(error)


@app.errorhandler(400)
def bad_request(error):
    """ Handles requests that have bad or malformed data """
    return jsonify(status=400, error='Bad Request', message=error.message), 400


@app.errorhandler(404)
def not_found(error):
    """ Handles products that cannot be found """
    return jsonify(status=404, error='Not Found', message=error.message), 404


@app.errorhandler(405)
def method_not_supported(error):
    """ Handles bad method calls """
    return jsonify(status=405, error='Method not Allowed',
                   message='Your request method is not supported.' \
                           ' Check your HTTP method and try again.'), 405


@app.errorhandler(415)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=415, error='Unsupported media type', message=message), 415


@app.errorhandler(500)
def internal_server_error(error):
    """ Handles catostrophic errors """
    return jsonify(status=500, error='Internal Server Error', message=error.message), 500


######################################################################
# DECORATORS
######################################################################
def requires_content_type(*content_types):
    """ Use this decorator to check content type """
    def decorator(func):
        """ Inner decorator """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """ Checks that the content type is correct """
            for content_type in content_types:
                if request.headers['Content-Type'] == content_type:
                    return func(*args, **kwargs)

            app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
            abort(HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                  'Content-Type must be {}'.format(content_types))
        return wrapper
    return decorator


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Return some message of our API by default """
    return jsonify(name='Products REST API Service',
                   version='1.0',
                   url=url_for('list_products', _external=True)), HTTP_200_OK


######################################################################
# LIST PRODUCTS
######################################################################
@app.route('/products', methods=['GET'])
def list_products():
    """ Retrieves a list of products from the database """
    results = []
    keyword = request.args.get('keyword')
    if keyword:
        results = Product.catalog.query(keyword)
    else:
        results = Product.catalog.all()
    products = results
    sort_type = request.args.get('sort')
    if sort_type == 'price':
        """ Retrieves a list of products with the lowest price showed first from the database """
        results = sorted(products, key=lambda p: float(p.get_price()), reverse=False)
    elif sort_type == 'price-':
        """ Retrieves a list of products with the highest price showed first from the database """
        results = sorted(products, key=lambda p: float(p.get_price()), reverse=True)
    elif sort_type == 'review':
        """ Retrieves a list of products with the highest review showed first from the database """
        results = sorted(products, key=lambda p: p.avg_score(), reverse=True)
    elif sort_type == 'name':
        """ Retrieves a list of products in alphabetical order from the database """
        results = sorted(products, key=lambda p: p.get_name().lower(), reverse=False)
    elif sort_type == 'name-':
        """ Retrieves a list of products in reverse alphabetical order from the database """
        results = sorted(products, key=lambda p: p.get_name().lower(), reverse=True)

    return make_response(jsonify([product.serialize() for product in results]), HTTP_200_OK)


######################################################################
# RETRIEVE A PRODUCT BY ID
######################################################################
@app.route('/products/<int:id>', methods=['GET'])
def get_products(id):
    """ Retrieves a Product with a specific id """
    product = Product.catalog.find(id)
    if not product:
        abort(HTTP_404_NOT_FOUND, "Product with id '{}' was not found.".format(id))

    return make_response(jsonify(product.serialize()), HTTP_200_OK)


######################################################################
# ADD A NEW PRODUCT
######################################################################
@app.route('/products', methods=['POST'])
@requires_content_type('application/json', 'application/x-www-form-urlencoded')
def create_product():
    """
    Creates a product and saves it.
    This endpoint will create a Product based the data in the body that is posted
    or data that is sent via an html form post.
    """
    data = {}
    # Check for form submission data
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        app.logger.info('Processing FORM data')
        data = {
            "id": request.form['id'],
            "name": request.form['name'],
            "price": request.form['price'],
            "image_id": request.form['image_id'],
            "description": request.form['description'],
            "review_list": request.form['review_list'].split("\t")
        }
    else:
        app.logger.info('Processing JSON data')
        data = request.get_json()

    product = Product()  # this will auto generate an id for product
    product.deserialize(data)
    Product.catalog.save(product)
    message = product.serialize()
    return make_response(jsonify(message), HTTP_201_CREATED,
                  {'Location': url_for('get_products', product_id=product.id, _external=True)})


######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route('/products/<int:id>', methods=['PUT'])
@requires_content_type('application/json')
def update_products(id):
    """ Updates a product in the catalog """
    product = Product.catalog.find(id)

    if not product:
        abort(HTTP_404_NOT_FOUND, "Product with id '{}' was not found.".format(id))
    product.deserialize(request.get_json())
    Product.catalog.save()
    return make_response(jsonify(product.serialize()), HTTP_200_OK)


######################################################################
# DELETE A PRODUCT
######################################################################
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_products(id):
    """ Removes a Product from the database that matches the id """
    Product.catalog.delete(id)

    return make_response('', HTTP_204_NO_CONTENT)


######################################################################
#   U T I L I T Y   F U N C T I O N S
######################################################################

@app.before_first_request
def init_db(redis=None):
    """ Initlaize the model """
    Product.catalog.init_db(redis)


# load sample data
def data_load(payload):
    """ Loads a Product into the database """
    product = Product(**payload)
    Product.catalog.save(product)


def data_reset():
    """ Removes all Pets from the database """
    Product.catalog.remove_all()


def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print('Setting up logging...')
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
if __name__ == "__main__":
    print("*********************************")
    print(" P R O D U C T   S H O P   S E R V I C E ")
    print("*********************************")
    initialize_logging()
    phone_review_list = [Review(username="applefan", score="4", detail="OK"),
                         Review(username="helloworld", score="4", detail="As expected"),
                         Review(username="pythonfan", score="3", detail="So So")]
    pc_review_list = [Review(username="applelover", score="5", detail="Excellent"),
                      Review(username="tvfan", score="5", detail="Loving this!!"),
                      Review(username="devops team member", score="5", detail="Highly recommend!"),
                      Review(username="nyu", score="5", detail="Nice!")]
    Product.catalog.save(Product(0, "iPhone 8", 649, review_list=phone_review_list))
    Product.catalog.save(Product(0, "MacBook Pro", 1799, review_list=pc_review_list))
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
