import time
class Product:
    __id = ''
    __name = ''
    __price = 0.0
    __imageId = ''
    __description = ''
    __reviewsList = []
    
    def __init__(self, id, name, price):
        self.__id = id
	self.__name = name
	self.__price = price

    def getId(self):
        return self.__id

    def setId(self, id):
        self.__id = id

    def getName(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def getPrice(self):
        return self.__price

    def setPrice(self, price):
        self.__price = price

    def getImageId(self):
        return self.__imageId

    def setImageId(self, imageId):
        self.__ImageId = imageId

    def getDescription(self):
        return self.__description

    def setDescription(self, description):
        self.__description = description

    def getReviewsList(self):
        return self.__reviewsList

    def setReviewsList(self, reviewsList):
        self.__reviewsList = reviewsList
    


class Review:
    '''Customer Information'''
    __date = time.time()
    __detail = ''

    def __init__(self, date):
        self.__date = date

    def getDate(self):
        return self.__date

    def getDetail(self):
        return self.__detail

    def setDate(self, date):
        self.__date = date

    def setDetail(self, detail):
        self.__detail = detail
