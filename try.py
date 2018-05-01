from cerberus import Validator


class Catalog:
    def __init__(self, redis=None):
        """Redis handles storage as well as index, thread safety"""
        # Define the rules and validator according the rules.
        schema = {
            'id': {'type': 'integer'},
            'name': {'type': 'string', 'required': True},
            'price': {'type': 'integer', 'required': True},
            'image_id':{'type': 'string'},
            'description': {'type': 'string'},
            'review_list': {'type': 'list'}
        }
        self.validator = Validator(schema)


