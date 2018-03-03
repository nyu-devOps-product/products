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
from models import Product, DataValidationError
import server

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
        server.Product.catalog.save(Product(0, "iPhone 8", 649))
        server.Product.catalog.save(Product(1, "MacBook Pro", 1799))
        self.app = server.app.test_client()

    def tearDown(self):
        """ Runs after each test """
        server.Product.catalog.remove_all()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Products REST API Service')

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

    def test_delete_product(self):
        """ Delete a product that exists """
        # save the current number of products for later comparrison
        product_count = self.get_product_count()
        # delete a product
        resp = self.app.delete('/products/1', content_type='application/json')
        print resp
        
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_product_count()
        self.assertEqual(new_count, product_count - 1)


    def test_get_nonexisting_product(self):
        """ Get a product that doesn't exist """
        resp = self.app.get('/products/5')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_method_not_allowed(self):
        """ Call a Method thats not Allowed """
        resp = self.app.post('/products/0')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


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
