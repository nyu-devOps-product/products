"""
Models for Product catalog
All of the models are stored in this module
Models
------
Catalog - A catalog used in the database
Product - save product value
Review  - A review used in product store
"""

import threading
import re


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Catalog(object):
    """
    Class that represents a Catalog
    """

    def __init__(self):
        self.data = []
        self.index = -1
        self.lock = threading.Lock()

    def next_index(self):
        with self.lock:
            self.index += 1
        return self.index

    def save(self, product):
        """
        Saves a Product to the data store
        This includes save a new Product or Update a product with the same id
        """
        if product.id < 0:
            product.set_id(self.next_index())
        else:
            for i in range(len(self.data)):
                if self.data[i].id == product.id:
                    self.data[i] = product
                    return
        self.data.append(product)

    def all(self):
        """ Returns all of the Products in the database """
        # return a `copy` of data
        return [product for product in self.data]

    def find(self, id):
        """ Find a Product by its ID """
        if not self.data:
            return None
        products = [product for product in self.data if str(
            product.id) == str(id)]
        if products:
            return products[0]
        return None

    def delete(self, id):
        """ Removes a product with a specific id from the data store """
        product = self.find(id)

        if product:
            self.data.remove(product)

    def query(self, keyword, value):
        """ Find Products by keyword """
        found = []
        pattern = r'.*?{0}.*?'.format(value)
        for product in self.all():
            fields = product.serialize()
            match = re.search(pattern, str(fields[keyword]).lower())
            if match:
                found.append(product)

        return found

    def remove_all(self):
        """ Removes all of the products from the database """
        del self.data[:]
        self.index = -1
        return self.data


class Product(object):
    """
    Class represents a product

    required parameters: name, price. If id isn't specified, it will be
    auto-incremented when added to Catalog
    """

    # static variable
    catalog = Catalog()

    def __init__(self, name, price, id=-1, image_id='', description='', review_list=None):
        self.id = id
        self.name = name
        self.price = price
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
        result = {"id": self.id, "name": self.name, "price": self.price, "image_id": self.image_id,
                  "description": self.description,
                  "review_list": [review.serialize() for review in self.review_list]}
        return result

    def deserialize(self, data):
        """
        Deserializes a product from a dictionary
        Args:
            data (dict): A dictionary containing the product data
        """
        if not isinstance(data, dict):
            raise DataValidationError(
                'Invalid pet: body of request contained bad or no data')
        # Set required attributes:
        try:
            self.name = data['name']
            self.price = data['price']
        except KeyError as err:
            raise DataValidationError(
                'Invalid product: missing ' + err.args[0])
        # Set optional attributes:
        for attribute in data:
            if attribute not in ['name', 'price']:
                if hasattr(self, attribute):
                    setattr(self, attribute, data[attribute])
                else:
                    raise DataValidationError(
                        'Invalid product: unknown attribute ' + attribute)
        return

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

    def __init__(self, username, score, date='', detail=''):
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
        result = {"username": self.username, "date": self.date,
                  "score": self.score, "detail": self.detail}
        return result
