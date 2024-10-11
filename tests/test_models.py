# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        '''It should read a product'''
        product = ProductFactory()
        app.logger.info(f'Reading product {product}')
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product_new = Product.find(product.id)
        self.assertEqual(product_new.id, product.id)
        self.assertEqual(product_new.name, product.name)
        self.assertEqual(product_new.description, product.description)
        self.assertEqual(product_new.available, product.available)
        self.assertEqual(product_new.price, product.price)
        self.assertEqual(product_new.category, product.category)

    def test_update_a_product(self):
        '''It should update a product'''
        product = ProductFactory()                                           # Create product
        app.logger.info(f'Creating product {product}')
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        app.logger.info(f'Created product {product}')
        product.description = "New description"                              # Change description and update
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "New description")
        all_products = Product.all()                  # Check only one fetched item and description updated.
        self.assertEqual(len(all_products), 1)
        self.assertEqual(all_products[0].id, original_id)
        self.assertEqual(all_products[0].description, "New description")

    def test_delete_a_product(self):
        '''It should delete a product'''
        product = ProductFactory()                                           # Create product
        app.logger.info(f'Creating product {product}')
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        all_products = Product.all()                                         # Check only one fetched item
        self.assertEqual(len(all_products), 1)
        all_products[0].delete()
        all_products = Product.all()                                         # Confirm no more products in database
        self.assertEqual(len(all_products), 0)

    def test_list_all_products(self):
        '''It should list all products'''
        all_products = Product.all()                                         # Confirm no products in database
        self.assertEqual(len(all_products), 0)
        for _ in range(5):
            product = ProductFactory()                                       # Create 5 product
            app.logger.info(f'Creating product {product}')
            product.id = None
            product.create()
        all_products = Product.all()                                         # Confirm 5 products in database
        self.assertEqual(len(all_products), 5)

    def test_find_product_by_name(self):
        '''It should find products by name'''
        all_products = ProductFactory.create_batch(5)                        # Create batch of 5
        for product in all_products:
            product.create()
        product0_name = all_products[0].name                                 # Get product 1 name
        counter = 0
        for product in all_products:
            if product.name == product0_name:
                counter += 1
        products_with_name0 = Product.find_by_name(product0_name)            # Find all products with same name
        self.assertEqual(products_with_name0.count(), counter)                  # Check if count matches expected
        for product in products_with_name0:                                  # Check all names match
            self.assertEqual(product.name, product0_name)

    def test_find_product_by_availability(self):
        '''It should find products by availability'''
        all_products = ProductFactory.create_batch(10)                       # Create batch of 10
        for product in all_products:
            product.create()
        product0_avail = all_products[0].available                           # Get product 1 availability
        counter = 0
        for product in all_products:
            if product.available == product0_avail:
                counter += 1
        products_with_avail0 = Product.find_by_availability(product0_avail)  # Find all products with same availability
        self.assertEqual(products_with_avail0.count(), counter)              # Check if count matches expected
        for product in products_with_avail0:                                 # Check all availabilities match
            self.assertEqual(product.available, product0_avail)

    def test_find_product_by_cat(self):
        '''It should find products by category'''
        all_products = ProductFactory.create_batch(10)                        # Create batch of 10
        for product in all_products:
            product.create()
        product0_cat = all_products[0].category                               # Get product 1 category
        counter = 0
        for product in all_products:
            if product.category == product0_cat:
                counter += 1
        products_with_cat0 = Product.find_by_category(product0_cat)            # Find all products with same category
        self.assertEqual(products_with_cat0.count(), counter)                  # Check if count matches expected
        for product in products_with_cat0:                                  # Check all category matches
            self.assertEqual(product.category, product0_cat)

    def test_find_by_price(self):
        '''It should find products by price'''
        all_products = ProductFactory.create_batch(10)                       # Create batch of 10
        for product in all_products:
            product.create()
        product0_price = all_products[0].price                               # Get product 1 price
        counter = 0
        for product in all_products:
            if product.price == product0_price:
                counter += 1
        products_with_price0 = Product.find_by_price(product0_price)      # Find all products with same price
        self.assertEqual(products_with_price0.count(), counter)              # Check if count matches expected
        for product in products_with_price0:                                 # Check all price matches
            self.assertEqual(product.price, product0_price)

    def test_update_data_valid_handler(self):
        '''It should handle data validation error when updating
        without id'''
        product = ProductFactory()                                           # Create product
        app.logger.info(f'Creating product {product}')
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        app.logger.info(f'Created product {product}')
        product.description = "New description"                              # Change description and update
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_find_price_str_handler(self):
        '''It should handle price in strings gracefully'''
        all_products = ProductFactory.create_batch(10)                       # Create batch of 10
        for product in all_products:
            product.create()
        product0_price = all_products[0].price                               # Get product 1 price
        counter = 0
        for product in all_products:
            if product.price == product0_price:
                counter += 1
        products_with_price0 = Product.find_by_price(str(product0_price))    # Find all products with same price (when in str)
        self.assertEqual(products_with_price0.count(), counter)              # Check if count matches expected
        for product in products_with_price0:                                 # Check all price matches
            self.assertEqual(product.price, product0_price)

    def test_deserialize_error(self):
        '''Check deserialization error handlers'''
        product = ProductFactory()
        data = product.serialize()
        data['available'] = 42
        self.assertRaises(DataValidationError, lambda: product.deserialize({}))
        self.assertRaises(DataValidationError, lambda: product.deserialize(data))
        product = ProductFactory()
        data = product.serialize()
        data['price'] = {}
        self.assertRaises(DataValidationError, lambda: product.deserialize(data))
