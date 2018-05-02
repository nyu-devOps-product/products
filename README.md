# products 

[![Build Status](https://travis-ci.org/DevOps-Squads-Spring-2018/products.svg?branch=master)](https://travis-ci.org/DevOps-Squads-Spring-2018/products)
[![codecov](https://codecov.io/gh/DevOps-Squads-Spring-2018/products/branch/master/graph/badge.svg)](https://codecov.io/gh/DevOps-Squads-Spring-2018/products)

This repo is a resource for products implementing a RESTful API using Python Flask. It contains methods to create, update, delete, access, list, search for and sort products using attributes such as `name`, `price`, `review score`, `description` and the likes. This resource model has no persistence to keep the application simple.

## Prerequisite Installation using Vagrant

The easiest way to use this repo is with Vagrant and VirtualBox. if you don't have this software, the first step is to download and install it:

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Clone the project to your development folder and create your Vagrant vm

    $ git clone https://github.com/DevOps-Squads-Spring-2018/products.git
    $ cd products
    $ vagrant up

Once the VM is up you can use it with:

    $ vagrant ssh
    $ cd /vagrant
    $ python server.py

When you are done, you can use `Ctrl+C` to stop the server and then exit and shut down the vm with:

    $ exit
    $ vagrant halt

If the VM is no longer needed you can remove it with:

    $ vagrant destroy

## List of available calls

### 1. List all products
  Retrieves a list of all products from the product catalog.

  `GET /products`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** if there are products to return: `{ name: "product-name", price: "product-price", optional-attributes: "opt" }`; otherwise empty list.

### 2. Read a Product
  Retrieves a product using its `id`.

  `GET /products/id`
  
*  **URL Params**

   **Required:**
 
   `id` in `/products/id`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ name: "product-name", price: "product-price", id: "id", optional-attributes: "opt" }`
 
* **Error Response:**

  * **Code:** 404 NOT FOUND <br />
    **Content:** `{ error: product with id: id was not found }`

### 3. Create a Product
  Creates a product and saves it into the Product Catalog.

  `POST /products`

*  **Data Params**

   **Required:**
 
   `name` -- product name
   
   `price` -- product price
   
   **Optional:**
   
   `id` -- product id; by default, it gets autoincremented for all products in catalog starting at 0
   
   `image_id` -- product image id
   
   `description` -- product description string
   
   `review_list` -- list of Review classes for the Product; by default it's an empty list

* **Success Response:**

  * **Code:** 201 CREATED <br />
    **Content:** `{ name: "new-product-name", price: "new-product-price", id: "id", optional-attributes: "opt" }`
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST

### 4. Update a Product
  Updates an existing product from the Product Catalog.

  `PUT /products/id`
  
*  **URL Params**

   **Required:**
 
   `id` in `/products/id`

*  **Data Params**

   **Required:**
 
   `name` -- product name
   
   `price` -- product price
   
   **Optional:**
   
   `id` -- product id; by default, it gets autoincremented for all products in catalog starting at 0
   
   `image_id` -- product image id
   
   `description` -- product description string
   
   `review_list` -- list of Review classes for the Product; by default it's an empty list


* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** `{ name: "updated-product-name", price: "updated-product-price", id: "id", optional-attributes: "opt" }`
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST
    **Content:** `{ error: 'Product with id: id was not found' }`
  
### 5. Delete a Product
  Deletes a product from the Product Catalog using its id.
  
  `DELETE /products/id`

*  **URL Params**

   **Required:**
 
   `id` in `/products/id`

* **Success Response:**

  * **Code:** 204 NO CONTENT


### 6. Query products by keyword
  Retrieves a subset of products from the catalog that match `keyword`.

  `GET /products`
  
*  **Data Params**

   **Optional:**
 
   `keyword=[query]` -- search query which generates a subset of products that match `keyword`
   
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** if there are products to return: `{ name: "product-name", price: "product-price", optional-attributes: "opt" }`; otherwise empty list.
    
    
### 7. Sort products
  Sorts products from the catalog based on `name`, `price` or `review score`. Can be combined with **Query products by keyword** using attribute `keyword`.

  `GET /products`

*  **Data Params**

   **Optional:**
   
   `sort=[sort-method]` -- sort results by name, price or review score. Possible values for `sort-method` are:
   * `price`: sort by price from low to high;
   * `price-`: sort by price from high to low;
   * `name`: sort by product name in alphabetical order;
   * `name-`: sort by product name in reverse alphabetical order;
   * `review`: sort by review score of the products showing highest review scores first.

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** if there are products to return: `{ name: "product-name", price: "product-price", optional-attributes: "opt" }`; otherwise empty list.

### 8. Review product
  Posts a review for product with id `id`.

  `PUT /products`

*  **Data Params**

   **Required:**
 
   `username` -- username
   
   `score` -- review score for product
   
   **Optional:**
   
   `date` -- date when review was posted
   
   `detail` -- more detailed review

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ name: "product-name", price: "product-price", review_list: [list of review including the new one] }`

## Running tests locally

There is no need to run the tests locally because Travis Ci is set up on this repo to run them for you, but if you wish to run them locally after doing the prerequisite installations, you can run the following commands:

    $ cd products
    $ vagrant up
    $ vagrant ssh
    $ cd /vagrant
    $ nosetests

(If running from a Windows machine, in the last command you should specify the `--exe` flag as follows: `nosetests --exe`.) Running the tests should give you a good indication that the unit tests are passing that that there is good code coverage.

## What's included in this project?

    * server.py -- the main service using Python Flask
    * tests/test_server.py -- unit test cases against the service
    * models.py -- contains model definitions for the resource (e.g. Product, Catalog, Review)
    * tests/test_model.py -- unit test cases against the Product model
    * .travis.yml -- the Travis CI file that automates testing

This repo is part of the CSCI-GA.3033-013 DevOps course taught by John Rofrano at NYU Courant Institute of Mathematical Sciences, New York in Spring 2018.
