"""
Product Service Runner

Start the Product Service and initializes logging
"""

import os
from app import app, server
from app.server import Review, Product

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print "****************************************"
    print " P R O D U C T   S E R V I C E   R U N N I N G"
    print "****************************************"
    server.initialize_logging()
    # phone_review_list = [Review(username="applefan", score="4", detail="OK"),
    #                      Review(username="helloworld",
    #                             score="4", detail="As expected"),
    #                      Review(username="pythonfan", score="3", detail="So So")]
    # pc_review_list = [Review(username="applelover", score="5", detail="Excellent"),
    #                   Review(username="tvfan", score="5",
    #                          detail="Loving this!!"),
    #                   Review(username="devops team member",
    #                          score="5", detail="Highly recommend!"),
    #                   Review(username="nyu", score="5", detail="Nice!")]
    # Product.catalog.save(
    #     Product("iPhone 8", 649, 0, review_list=phone_review_list))
    # Product.catalog.save(
    #     Product("MacBook Pro", 1799, 1, review_list=pc_review_list))
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
