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

WAIT_SECONDS = 30
BASE_URL = getenv('BASE_URL', 'http://localhost:5000/')

@given(u'the following products')
def step_impl(context):
    """ Delete all Products and load three new ones """
    headers = {'Content-Type': 'application/json'}
    # Get all products and delete them from catalog:
    context.resp = requests.get(context.base_url + '/products')
    # Delete any product that may be in the catalog
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
            "id": int(row['id']),
            "name": row['name'],
            "price": int(row['price']),
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
    context.driver.get(context.base_url)

@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)#(message)

@then(u'I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)

@when(u'I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then(u'I should see "{name}" in the results')
def step_impl(context, name):
    # element = context.driver.find_element_by_id('search_results')
    # expect(element.text).to_contain(name)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    expect(found).to_be(True)

@then(u'I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then(u'I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = 'product_' + element_name.lower()
    #element = context.driver.find_element_by_id(element_id)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    #expect(element.get_attribute('value')).to_equal(text_string)
    expect(found).to_be(True)

@when(u'I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = 'product_' + element_name.lower()
    #element = context.driver.find_element_by_id(element_id)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)

@then(u'I should see the message "{message}"')
def step_impl(context, message):
    #element = context.driver.find_element_by_id('flash_message')
    #expect(element.text).to_contain(message)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)
