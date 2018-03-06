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
Test cases for product Model
Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
from models import Product, DataValidationError, Review

######################################################################
#  T E S T   C A S E S
######################################################################
class TestProducts(unittest.TestCase):
    """ Test Cases for Products """

    def setUp(self):
        Product.catalog.remove_all()
        self.product = Product(name="iPhone", price="649")

    def test_create_a_product(self):
        """ Create a product and assert that it exists """
        self.assertTrue(self.product != None)
        self.assertEqual(self.product.name, "iPhone")
        self.assertEqual(self.product.price, "649")

    def test_product_setter_getter_methods(self):
        """ Set and get all product attributes """
        product = Product(name="Samsung", price="499")
        product.set_name("Samsung HDTV")
        product.set_price("449")
        product.set_id("0")
        product.set_image_id("001")
        product.set_description("Latest TV")
        review = Review(username="couchpotato123", score="5", detail="Fantastic TV")
        review_list = [review]
        product.set_review_list(review_list)
        self.assertEqual(product.get_name(), "Samsung HDTV")
        self.assertEqual(product.get_price(), "449")
        self.assertEqual(product.get_id(), "0")
        self.assertEqual(product.get_image_id(), "001")
        self.assertEqual(product.get_description(), "Latest TV")
        self.assertEqual(product.get_description(), "Latest TV")
        self.assertEqual(product.get_review_list(), review_list)

    def test_review_setter_getter_methods(self):
        """ Set and get all Review attributes """
        review = Review(username="couchpotato123", score="3")
        review.set_username("furiouscouchpotato123")
        review.set_score("1")
        review.set_detail("Worst. TV. Ever.")
        review.set_date("4-3-2018")
        self.assertEqual(review.get_username(), "furiouscouchpotato123")
        self.assertEqual(review.get_score(), "1")
        self.assertEqual(review.get_detail(), "Worst. TV. Ever.")
        self.assertEqual(review.get_date(), "4-3-2018")

    def test_add_a_product(self):
        """ Create a product and add it to the catalog """
        products = Product.catalog.all()
        self.assertEqual(products, [])
        self.assertTrue(self.product != None)
        Product.catalog.save(self.product)
        # Assert that it was assigned an id and was added to the catalog
        self.assertEqual(self.product.id, 0)
        products = Product.catalog.all()
        self.assertEqual(len(products), 1)

    def test_update_a_product(self):
        """ Update a product """
        Product.catalog.save(self.product)
        self.assertEqual(self.product.id, 0)
        # Update product and save it
        self.product.price = "599"
        Product.catalog.save(self.product)
        # Fetch it back and make sure the id hasn't changed, but the data has
        self.assertEqual(self.product.id, 0)
        products = Product.catalog.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].price, "599")

    def test_delete_a_product(self):
        """ Delete a product """
        Product.catalog.save(self.product)
        self.assertEqual(len(Product.catalog.all()), 1)
        # delete the product and make sure it isn't in the catalog
        Product.catalog.delete(self.product.id)
        self.assertEqual(len(Product.catalog.all()), 0)

    def test_serialize_a_product(self):
        """ Test serialization of a product """
        self.product.set_id(0)
        data = self.product.serialize()
        self.assertNotEqual(data, None)
        self.assertEqual(data['id'], 0)
        self.assertEqual(data['name'], "iPhone")
        self.assertEqual(data['price'], "649")

    def test_deserialize_a_product(self):
        """ Test deserialization of a product """
        data = {"name":"iPhone", "price":"649", "id":"0", "image_id":"0005", "description":"Latest phone model."}
        product = Product(name="Samsung", price="749")
        product.deserialize(data)
        self.assertNotEqual(product, None)
        # Must be the same from the deserialized object:
        self.assertEqual(product.name, "iPhone")
        self.assertEqual(product.price, "649")
        self.assertEqual(product.id, "0")
        self.assertEqual(product.image_id, "0005")
        self.assertEqual(product.description, "Latest phone model.")

    def test_deserialize_without_required_fields(self):
        """ Deserialize a product without all required fields """
        # Should fail deserializing a product with missing name (required attribute):
        data = {"price":"649", "id":"0"}
        self.assertRaises(DataValidationError, self.product.deserialize, data)
        # Should fail deserializing a product with missing price (required attribute):
        data = {"name":"iPhone", "id":"0"}
        self.assertRaises(DataValidationError, self.product.deserialize, data)
        # Should successfully deserialize product with all required fields:
        data = {"name":"Samsung", "price":"900"}
        self.product.deserialize(data)
        self.assertEqual(self.product.name, "Samsung")
        self.assertEqual(self.product.price, "900")

    def test_deserialize_with_bad_attributes(self):
        """ Deserialize a product with bad attributes """
        data = {"name":"Samsung", "price":"900", "id":"0", "bad_attribute":"740"}
        self.assertRaises(DataValidationError, self.product.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a product with no data """
        self.assertRaises(DataValidationError, self.product.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserailize a product with bad data """
        self.assertRaises(DataValidationError, self.product.deserialize, "data")

    def test_find_product(self):
        """ Find a product by ID """
        product1 = Product(name="iPhone", price="649", id="0")
        product2 = Product(name="Samsung", price="749", id="1")
        Product.catalog.save(product1)
        Product.catalog.save(product2)
        product = Product.catalog.find(1)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, "1")
        self.assertEqual(product.name, "Samsung")
        self.assertEqual(product.price, "749")

    def test_find_with_no_products(self):
        """ Find a product with no products """
        product = Product.catalog.find(1)
        self.assertIs(product, None)

    def test_product_not_found(self):
        """ Test for a product that doesn't exist """
        self.product.set_id(0)
        Product.catalog.save(self.product)
        product = Product.catalog.find(1)
        self.assertIs(product, None)

    def test_query_product(self):
        """ Query a product by Keyword """
        Product.catalog.save(self.product)
        match = Product.catalog.query("iPhone")
        self.assertEqual(1, len(match))
        product1 = Product(name="asdqweiPhone123", price="649", id="0")
        Product.catalog.save(product1)
        match = Product.catalog.query("iPhone")
        self.assertEqual(2, len(match))

    def test_get_review_avg_score(self):
        """ Get average score for a list of reviews """
        watch_review_list = [Review(username="applefan", score="4", detail="OK"),
        Review(username="helloworld", score="4", detail="As expected"),
        Review(username="pythonfan", score="3", detail="So So")]
        watch = Product(name="I Watch", price=329, id="2", image_id="001", review_list=watch_review_list)
        avg_score = float(4+4+3)/3
        watch.set_review_list(watch_review_list)
        Product.catalog.save(watch)
        w = Product.catalog.find(2)
        self.assertEquals(Product.avg_score(w), avg_score)

    def test_get_review_avg_score_empty_reviews_list(self):
        """ Get average score for an empty list of reviews """
        self.assertEquals(self.product.review_list, [])
        self.assertEqual(Product.avg_score(self.product), 0.0)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestPets)
    # unittest.TextTestRunner(verbosity=2).run(suite)