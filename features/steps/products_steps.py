"""
Product Steps

Steps file for products.feature
"""
from os import getenv
import json
import ast
import requests
from behave import *
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import server

WAIT_SECONDS = 30
BASE_URL = getenv('BASE_URL', 'http://localhost:5000/')

@given(u'the following products')
def step_impl(context):
    """ Delete all Products and load three new ones """
    headers = {'Content-Type': 'application/json'}
    # Get all products and delete them from catalog:
    context.resp = requests.get(context.base_url + '/products')
    for i in json.loads(context.resp.content):
        id = i['id']
        context.resp = requests.delete(context.base_url + '/products/' + str(id), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    context.resp = requests.get(context.base_url + '/products')
    # Ensure all products have been deleted:
    list_products = ast.literal_eval(context.resp.content)
    expect(len(list_products)).to_equal(0)
    create_url = context.base_url + '/products'
    # Parse products from products.feature and add them to catalog:
    for row in context.table:
        data = {
            "id": row['id'],
            "name": row['name'],
            "price": row['price'],
            "image_id": row['image_id'],
            "description": row['description']
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
    # Ensure the products have been added to the catalog
    context.resp = requests.get(context.base_url + '/products')
    list_products = ast.literal_eval(context.resp.content)
    expect(len(list_products)).to_equal(3)

@when(u'I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    print(dir(context))
    context.driver.get(context.base_url)
    #context.driver.save_screenshot('home_page.png')
