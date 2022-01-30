import json
from lib2to3.pytree import Base
from urllib import request
from tornado.web import RequestHandler, HTTPError, MissingArgumentError
from databases.core import Connection
from . import queries
import base64
from urllib.parse import quote, unquote


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


def generate_key(json_: str) -> str:
    """generate base64 encoded key build by json using "key1+value1+key2+..." method

    Args:
        json_ (str)

    Returns:
        bytes: key
    """
    encoded_string = ''.join([f'{key}{value}' for key, value in json.loads(json_).items()])
    return base64.urlsafe_b64encode(encoded_string.encode('utf-8')).decode('utf-8')


class BaseHandler(RequestHandler):
    """
    base class for handlers
    """

    def initialize(self, connection: Connection):
        self.connection = connection

    # override error page
    def write_error(self, status_code: int, **kwargs) -> None:
        self.finish(json.dumps({
            'error': f'{status_code} {self._reason}'
        }))

    # set header
    def prepare(self):
        self.set_header('Content-Type', 'application/json')
    

class BaseHandlerParseKey(BaseHandler):
    def prepare(self):
        try:
            self.key = self.get_query_argument('key')
        except MissingArgumentError:
            raise HTTPError(400)
        # key is url-encoded so need to decode
        self.key = unquote(self.key)
        return super().prepare()


class RequestAddHandler(BaseHandler):
    async def post(self):
        # validate json
        if not validate_json(self.request.body):
            raise HTTPError(400)

        # clean json and generate key
        json_ = clear_json(self.request.body)
        key = generate_key(json_)

        # insert/update in database
        async with self.connection:
            await queries.insert_request(self.connection, key, json_)

        # key url-encoded because it may contain "="
        # so it can be used in get request in url
        self.write(json.dumps({'key': quote(key)}))


class RequestGetHandler(BaseHandlerParseKey):
    async def get(self):
        # get request from database
        async with self.connection:
            request = await queries.get_request(self.connection, self.key)
        
        if request is None:
            raise HTTPError(404)

        # make response
        json_ = json.loads(request['body'])
        json_['duplicates'] = request['duplicates']

        self.write(json.dumps(json_))


class RequestDeleteHandler(BaseHandlerParseKey):
    async def delete(self):
        async with self.connection:
            deleted = await queries.delete_request(self.connection, str(self.key))

        if deleted:
            self.write(json.dumps({'key': quote(str(self.key))}))
        else:
            raise HTTPError(404)
        

class RequestUpdateHandler(BaseHandlerParseKey):
    async def put(self):
        # validate json
        if not validate_json(self.request.body):
            raise HTTPError(400)

        # clean json and generate key
        json_ = clear_json(self.request.body)
        key = generate_key(json_)

        async with self.connection:
            updated = await queries.update_request(self.connection, self.key, key, json_)

        if updated:
            self.write(json.dumps({'key': quote(str(key))}))
        else:
            raise HTTPError(404)

class GetStaticticsHandler(BaseHandler):
    async def get(self):
        async with self.connection:
            statistics = await queries.get_statistics(self.connection)

        try:
            percentage = 100 / float(statistics['sum_all'] or 0) * float(statistics['sum_duplicates'] or 0)
        except ZeroDivisionError:
            percentage = 0
        return self.write(json.dumps({'percentage': round(percentage, 2)}))