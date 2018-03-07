import os
import re
import json
import logging
import pickle
from redis import Redis
from redis.exceptions import ConnectionError

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


# This Catalog is the initial version using in-memory storage
class Catalog:
    def __init__(self, redis=None):
        """Redis handles storage as well as index, thread safety"""
        """ interface to database """
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
            if key != 'index':  # filer out our id index
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

    def query(self, keyword):
        """ Query/Find Products by keyword """
        found = []
        logger.info('Processing query for %s', keyword)
        if isinstance(keyword, str):
            keyword = keyword.lower()  # make case insensitive

        pattern = r'.*?{0}.*?'.format(keyword)
        for key in self.redis.keys():
            if key != 'index':  # filer out our id index
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


class Product:
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
        return self.id

    def set_id(self, id):
        self.id = id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_price(self):
        return self.price

    def set_price(self, price):
        self.price = price

    def get_image_id(self):
        return self.image_id

    def set_image_id(self, image_id):
        self.image_id = image_id

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_review_list(self):
        return self.review_list

    def set_review_list(self, review_list):
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
        if not isinstance(data, dict):
            raise DataValidationError('Invalid pet: body of request contained bad or no data')
        # Set required attributes:
        try:
            # note "id" is immutable
            self.name = data['name']
            self.price = data['price']
        except KeyError as err:
            raise DataValidationError('Invalid product: missing ' + err.args[0])
        except TypeError as err:
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
        if len(self.review_list) == 0:
            return 0.0
        for review in self.review_list:
            count += 1
            res += float(review.get_score())
        return res / count


class Review:
    def __init__(self, username='', score=0, date='', detail=''):
        self.username = username
        self.score = score
        self.date = date
        self.detail = detail

    def get_username(self):
        return self.username

    def get_date(self):
        return self.date

    def get_score(self):
        return self.score

    def get_detail(self):
        return self.detail

    def set_username(self, username):
        self.username = username

    def set_date(self, date):
        self.date = date

    def set_score(self, score):
        self.score = score

    def set_detail(self, detail):
        self.detail = detail

    def serialize(self):
        result = {"date": self.date, "score": self.score, "detail": self.detail}
        return result
