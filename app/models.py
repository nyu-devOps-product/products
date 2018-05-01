"""
Models for Product catalog
All of the models are stored in this module
Models
------
Catalog - A catalog used in the database
Product - save product value
Review  - A review used in product store
"""

import os
import re
import json
import logging
import pickle
from cerberus import Validator
from redis import Redis
from redis.exceptions import ConnectionError
from custom_exceptions import DataValidationError

logger = logging.getLogger(__name__)


class Catalog:
    def __init__(self, redis=None):
        """Redis handles storage as well as index, thread safety"""
        # Define the rules and validator according the rules.
        schema = {
            'id': {'type': 'integer'},
            'name': {'type': 'string', 'required': True},
            'price': {'type': 'integer', 'required': True},
            'image_id':{'type': 'string'},
            'description': {'type': 'string'},
            'review_list': {'type': 'list'}
        }
        self.validator = Validator(schema)
        self.redis = redis

    # TODO: finish connecting to Redis

    def next_index(self):
        """ Increments the index and returns it """
        return self.redis.incr('index')

    def save(self, product):
        """
        Saves a Product to the data store
        This includes save a new Product or Update a product with the same id
        """
        if product.name is None:
            raise DataValidationError('name attribute is not set and it is required')
        if product.id <= 0:
            product.set_id(self.next_index())

        self.redis.set(product.id, pickle.dumps(product.serialize()))

    def all(self):
        """ Returns all of the Products in the database """
        # return a `copy` of data
        results = []
        for key in self.redis.keys():
            if key != 'index':  # filter out our id index
                data = pickle.loads(self.redis.get(key))
                product = Product(id=data['id']).deserialize(data)
                results.append(product)
        return results

    def find(self, id):
        """ Find a Product by its ID """
        if self.redis.exists(id):
            data = pickle.loads(self.redis.get(id))
            product = Product(id=data['id']).deserialize(data)
            return product
        return None

    def delete(self, id):
        self.redis.delete(id)

    def remove_all(self):
        self.redis.flushall()

    def query(self, keyword):
        """ Query/Find Products by keyword """
        found = []
        logger.info('Processing query for %s', keyword)
        if isinstance(keyword, str):
            keyword = keyword.lower()  # make case insensitive

        pattern = r'.*?{0}.*?'.format(keyword)
        for key in self.redis.keys():
            if key != 'index':  # filter out our id index
                data = pickle.loads(self.redis.get(key))
                for ele in data:
                    if ele != "review_list":
                        match = re.search(pattern, str(data[ele]))
                        if match:
                            found.append(Product(id=data['id']).deserialize(data))
                            break
        return found

    def remove_all(self):
        """ Removes all of the products from the database """
        self.redis.flushall()

######################################################################
#  R E D I S   D A T A B A S E   C O N N E C T I O N   M E T H O D S
######################################################################

    def init_db(self, redis=None):
        """
        Initialized Redis database connection
        This method will work in the following conditions:
          1) In Bluemix with Redis bound through VCAP_SERVICES
          2) With Redis running on the local server as with Travis CI
          3) With Redis --link in a Docker container called 'redis'
          4) Passing in your own Redis connection object
        Exception:
        ----------
          redis.ConnectionError - if ping() test fails
        """
        if redis:
            logger.info("Using client connection...")
            self.redis = redis
            try:
                self.redis.ping()
                logger.info("Connection established")
            except ConnectionError:
                logger.error("Client Connection Error!")
                self.redis = None
                raise ConnectionError('Could not connect to the Redis Service')
            return

        # Get the credentials from the Bluemix environment
        if 'VCAP_SERVICES' in os.environ:
            logger.info("Using VCAP_SERVICES...")
            vcap_services = os.environ['VCAP_SERVICES']
            services = json.loads(vcap_services)
            creds = services['rediscloud'][0]['credentials']
            logger.info("Conecting to Redis on host %s port %s",
                            creds['hostname'], creds['port'])
            self.connect_to_redis(creds['hostname'], creds['port'], creds['password'])
        else:
            logger.info("VCAP_SERVICES not found, checking localhost for Redis")
            self.connect_to_redis('127.0.0.1', 6379, None)
            if not self.redis:
                logger.info("No Redis on localhost, looking for redis host")
                self.connect_to_redis('redis', 6379, None)
        if not self.redis:
            # if you end up here, redis instance is down.
            logger.fatal('*** FATAL ERROR: Could not connect to the Redis Service')
            raise ConnectionError('Could not connect to the Redis Service')

    def connect_to_redis(self, hostname, port, password):
        """ Connects to Redis and tests the connection """
        logger.info("Testing Connection to: %s:%s", hostname, port)
        self.redis = Redis(host=hostname, port=port, password=password)
        try:
            self.redis.ping()
            logger.info("Connection established")
        except ConnectionError:
            logger.info("Connection Error from: %s:%s", hostname, port)
            self.redis = None
        return self.redis


class Product(object):
    """
    Class represents a product
    required parameters: name, price. If id isn't specified, it will be
    auto-incremented when added to Catalog
    """

    # static variable
    catalog = Catalog()

    # required parameters: name, price. If id isn't specified, it will be auto-incremented when added to Catalog
    def __init__(self, id=0, name=None, price=None, image_id='', description='', review_list=None):
        self.id = int(id)
        self.name = name
        self.price = int(price)
        self.image_id = image_id
        self.description = description
        if review_list is None:
            self.review_list = []
        else:
            self.review_list = review_list

    def get_id(self):
        """ Returns product id """
        return self.id

    def set_id(self, id):
        """ set product id """
        self.id = id

    def get_name(self):
        """ Returns product name """
        return self.name

    def set_name(self, name):
        """ set product name """
        self.name = name

    def get_price(self):
        """ Returns product price """
        return self.price

    def set_price(self, price):
        """ set product price """
        self.price = price

    def get_image_id(self):
        """ Returns product image_id """
        return self.image_id

    def set_image_id(self, image_id):
        """ set product image_id """
        self.image_id = image_id

    def get_description(self):
        """ Returns product description """
        return self.description

    def set_description(self, description):
        """ set product description """
        self.description = description

    def get_review_list(self):
        """ Returns product review_list """
        return self.review_list

    def set_review_list(self, review_list):
        """ set product review_list """
        self.review_list = review_list

    def serialize(self):
        """ Serializes a Product into a dictionary """
        result = {"id": self.id,
                  "name": self.name,
                  "price": self.price,
                  "image_id": self.image_id,
                  "description": self.description,
                  "review_list": [review.serialize() for review in self.review_list]
                  }
        return result

    def deserialize(self, data):
        """
        Deserializes a product from a dictionary
        Args:
            data (dict): A dictionary containing the product data
        """
        if isinstance(data, dict) and Product.catalog.validator.validate(data):
            self.name = data['name']
            self.price = data['price']
        else:
            raise DataValidationError('Invalid product: body of request contained bad or no data')

        # Set optional attributes:
        for attribute in data:
            if attribute not in ['name', 'price']:
                if hasattr(self, attribute):
                    setattr(self, attribute, data[attribute])
                else:
                    raise DataValidationError('Invalid product: unknown attribute ' + attribute)
        return self

    def avg_score(self):
        res = 0.0
        count = 0
        if not self.review_list:
            return 0.0
        for review in self.review_list:
            count += 1
            res += float(review.get_score())
        return res / count


class Review(object):
    """
    Class represents a review
    """
    def __init__(self, username='', score=0, date='', detail=''):
        self.username = username
        self.score = score
        self.date = date
        self.detail = detail

    def get_username(self):
        """ Returns Review username """
        return self.username

    def get_date(self):
        """ Returns Review date """
        return self.date

    def get_score(self):
        """ Returns Review score """
        return self.score

    def get_detail(self):
        """ Returns Review detail """
        return self.detail

    def set_username(self, username):
        """ set Review username """
        self.username = username

    def set_date(self, date):
        """ set Review date """
        self.date = date

    def set_score(self, score):
        """ set Review score """
        self.score = score

    def set_detail(self, detail):
        """ set Review detail """
        self.detail = detail

    def serialize(self):
        """ Serializes a Review into a dictionary """
        result = {"username": self.username,
                  "date": self.date,
                  "score": self.score,
                  "detail": self.detail}
        return result
