import threading
import time


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Catalog:
    def __init__(self):
        self.data = []
        self.index = -1
        self.lock = threading.Lock()

    # TODO: finish catalog
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
        products = [product for product in self.data if product.id == id]
        if products:
            return products[0]
        return None

    def delete(self, product):
        """ Removes a product from the data store """
        self.data.remove(self.find(product.id))

    def remove_all(self):
        """ Removes all of the products from the database """
        del self.data[:]
        self.index = -1
        return self.data

class Product:
    # static variable
    catalog = Catalog()

    # required parameters: name, price. If id is not specified, it will be auto-incremented when added to Catalog
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
        result = {"id": self.id, "name": self.name, "price": self.price, "image_id": self.image_id,
                  "description": self.description, "review_list": [review.serialize() for review in self.review_list]}
        return result


class Review:
    def __init__(self, date, score, detail=''):
        """ Customer Information """
        self.date = date
        self.score = score
        self.detail = detail

    def get_date(self):
        return self.date

    def get_score(self):
        return self.score

    def get_detail(self):
        return self.detail

    def set_date(self, date):
        self.date = date

    def set_score(self, score):
        self.score = score

    def set_detail(self, detail):
        self.detail = detail

    def serialize(self):
        result = {"date": self.date, "score": self.score, "detail": self.detail}
        return result
