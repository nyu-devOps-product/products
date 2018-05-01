# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for the product Service

Test cases can be run with:
  nosetests
  coverage report -m
"""

import logging
import unittest
import json
from flask_api import status    # HTTP Status Codes
from app.models import Product, Review
from app import server

######################################################################
#  T E S T   C A S E S
######################################################################


class TestProductServer(unittest.TestCase):
    """ product Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        server.app.debug = False
        server.initialize_logging(logging.ERROR)

    def setUp(self):
        """ Runs before each test """
        server.Product.catalog.remove_all()
        server.Product.catalog.save(Product(name="iPhone 8", price=649, id=0))
        server.Product.catalog.save(
            Product(name="MacBook Pro", price=1799, id=1))
        self.app = server.app.test_client()

    def tearDown(self):
        """ Runs after each test """
        server.Product.catalog.remove_all()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('Products RESTful Service', resp.data)

    def test_get_product_list(self):
        """ Get a list of products """
        resp = self.app.get('/products')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)

    def test_get_product(self):
        """ Get one product """
        resp = self.app.get('/products/0')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'iPhone 8')

    def test_get_product_not_found(self):
        """ Get a product thats not found """
        resp = self.app.get('/products/-1')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_product_none_in_list(self):
        """ Search for a product in a catalog with no products """
        server.Product.catalog.remove_all()
        resp = self.app.get('/products/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        # Ensure there are no products in the catalog:
        resp = self.app.get('/products')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)

    def test_create_product(self):
        """ Create a product """
        # save the current number of products for later comparison
        product_count = self.get_product_count()
        # add a new product
        new_product = {'name': 'samsung hdtv', 'price': '499'}
        data = json.dumps(new_product)
        resp = self.app.post('/products', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'samsung hdtv')
        self.assertEqual(new_json['price'], '499')
        # check that count has gone up and includes the new product
        resp = self.app.get('/products')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), product_count + 1)
        self.assertIn(new_json, data)

    def test_create_product_with_id(self):
        """ Create a product passing in an id """
        # add a new product
        new_product = {'name': 'sony vaio', 'price': '549', 'id': '2'}
        data = json.dumps(new_product)
        resp = self.app.post('/products', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'sony vaio')
        self.assertEqual(new_json['price'], '549')
        self.assertEqual(new_json['id'], '2')

    def test_create_product_with_missing_required_attribute(self):
        """ Create a product with the name missing (required attribute) """
        new_product = {'price': '550'}
        data = json.dumps(new_product)
        resp = self.app.post('/products', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product(self):
        """ Update a product using its id """
        new_product = {'name': 'sony vaio', 'price': '549'}
        data = json.dumps(new_product)
        # Update product with id 0:
        resp = self.app.put('/products/0', data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/products/0', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'sony vaio')
        self.assertEqual(new_json['price'], '549')

    def test_update_product_with_no_name(self):
        """ Update a product with missing name (required field) """
        new_product = {'price': '500'}
        data = json.dumps(new_product)
        resp = self.app.put('/products/1', data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_not_found(self):
        """ Update a product that can't be found """
        new_product = {"name": "Polaroid camera", "price": "55"}
        data = json.dumps(new_product)
        resp = self.app.put('/products/2', data=data,
                            content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_product_review(self):
        """ Review product """
        new_review = {"username": "Grumpy Grumperson",
                      "score": 1, "detail": "Can't stand it"}
        data = json.dumps(new_review)
        resp = self.app.put("products/0/review", data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/products/0', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['review_list'][-1]
                         ['username'], 'Grumpy Grumperson')

    def test_add_product_review_with_bad_attributes(self):
        """ Review product with bad attributes """
        new_review = {"badattribute1": "Grumpy Grumperson", "badattribute2": 1}
        data = json.dumps(new_review)
        resp = self.app.put("products/0/review", data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_inexistent_product_review(self):
        """ Review inexistent product """
        new_review = {"username": "Grumpy Grumperson", "score": 1}
        data = json.dumps(new_review)
        resp = self.app.put("products/2/review", data=data,
                            content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product(self):
        """ Delete a product that exists """
        # save the current number of products for later comparrison
        product_count = self.get_product_count()
        # delete a product
        resp = self.app.delete('/products/1', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_product_count()
        self.assertEqual(new_count, product_count - 1)

    def test_get_nonexisting_product(self):
        """ Get a product that doesn't exist """
        resp = self.app.get('/products/5')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_one_product(self):
        """ Get one product with keyword """
        resp = self.app.get('/products', query_string='keyword=iPhone')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertTrue('iPhone 8' in resp.data)
        self.assertFalse('MacBook Pro' in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['name'], 'iPhone 8')

    def test_method_not_allowed(self):
        """ Call a Method thats not Allowed """
        resp = self.app.post('/products/0')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_sort_by_lowest_price(self):
        """Show the product with the lowest price first"""
        resp = self.app.get('/products?sort=price')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data[0]['name'], 'iPhone 8')
        self.assertEqual(data[1]['name'], 'MacBook Pro')

    def test_sort_by_highest_price(self):
        """Show the product with the highest price first"""
        resp = self.app.get('/products?sort=price-')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data[0]['name'], 'MacBook Pro')
        self.assertEqual(data[1]['name'], 'iPhone 8')

    def test_sort_by_highest_review(self):
        """Show the product with the highest review first"""
        watch = Product(name="I Watch", price=329)
        watch.set_id("2")
        watch.set_image_id("001")
        watch.set_description("Smart Watch")
        watch_review_list = [Review(username="applefan", score="4", detail="OK"),
                             Review(username="helloworld",
                                    score="4", detail="As expected"),
                             Review(username="pythonfan",
                                    score="3", detail="So So")]
        watch.set_review_list(watch_review_list)
        server.Product.catalog.save(watch)
        self.assertEqual(watch.get_name(), "I Watch")
        self.assertEqual(watch.get_price(), 329)
        self.assertEqual(watch.get_id(), "2")
        self.assertEqual(watch.get_image_id(), "001")
        self.assertEqual(watch.get_description(), "Smart Watch")
        self.assertEqual(watch.get_review_list(), watch_review_list)
        tv = Product(name="Apple TV", price=9999)
        tv.set_id("3")
        tv.set_image_id("001")
        tv.set_description("Hi-end TV")
        tv_review_list = [Review(username="applelover", score="5", detail="Excellent"),
                          Review(username="tvfan", score="5",
                                 detail="Loving this!!"),
                          Review(username="devops team member",
                                 score="5", detail="Highly recommend!"),
                          Review(username="nyu", score="5", detail="Nice!")]
        tv.set_review_list(tv_review_list)
        server.Product.catalog.save(tv)
        self.assertEqual(tv.get_name(), "Apple TV")
        self.assertEqual(tv.get_price(), 9999)
        self.assertEqual(tv.get_id(), "3")
        self.assertEqual(tv.get_image_id(), "001")
        self.assertEqual(tv.get_description(), "Hi-end TV")
        self.assertEqual(tv.get_review_list(), tv_review_list)
        resp = self.app.get('/products?sort=review')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data[0]['name'], 'Apple TV')
        self.assertEqual(data[1]['name'], 'I Watch')

    def test_sort_by_alphabetical_order(self):
        """Show the product in alphabetical order"""
        resp = self.app.get('/products?sort=name')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data[0]['name'], 'iPhone 8')
        self.assertEqual(data[1]['name'], 'MacBook Pro')

    def test_sort_by_reverse_alphabetical_order(self):
        """Show the product in reverse alphabetical order"""
        resp = self.app.get('/products?sort=name-')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data[1]['name'], 'iPhone 8')
        self.assertEqual(data[0]['name'], 'MacBook Pro')


######################################################################
# Utility functions
######################################################################

    def get_product_count(self):
        """ save the current number of products """
        resp = self.app.get('/products')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
