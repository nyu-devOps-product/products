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
