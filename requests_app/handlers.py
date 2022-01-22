import json
from urllib import request
from tornado.web import RequestHandler, HTTPError, MissingArgumentError
from databases.core import Connection
from . import queries
import base64


def validate_json(json_: bytes) -> bool:
    """try to parse json and perform other checks to make sure it is valid

    Args:
        json_ (bytes): raw body with json
    """
    try:
        request = json.loads(json_)
    except json.JSONDecodeError:
        return False

    if not type(request) is dict:
        return False
    for value in request.values():
        if type(value) is list or type(value) is dict:
            return False

    return True


def clear_json(json_: bytes) -> str:
    """removes space-like characters or indentation

    Args:
        json_ (bytes): raw body with json

    Returns:
        str: cleaned json
    """
    return json.dumps(json.loads(json_))


def generate_key(json_: str) -> bytes:
    """generate base64 encoded key build by json using "key1+value1+key2+..." method

    Args:
        json_ (str)

    Returns:
        bytes: key
    """
    encoded_string = ''.join([f'{key}{value}' for key, value in json.loads(json_).items()])
    return base64.urlsafe_b64encode(encoded_string.encode('utf-8')).decode('utf-8')


class BaseHandler(RequestHandler):
    def initialize(self, connection: Connection):
        self.connection = connection


class RequestAddHandler(BaseHandler):
    async def post(self):
        if not validate_json(self.request.body):
            raise HTTPError(400)

        json_ = clear_json(self.request.body)
        key: bytes = generate_key(json_)
        async with self.connection:
            await queries.insert_request(self.connection, key, json_)

        self.write(json.dumps({'key': key}))

