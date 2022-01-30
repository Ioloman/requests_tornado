import os
import os.path
from databases import Database
from tornado.ioloop import IOLoop
import tornado.web
from tornado.httpserver import HTTPServer
from requests_app.handlers import (
    RequestAddHandler, 
    RequestGetHandler, 
    RequestDeleteHandler, 
    RequestUpdateHandler, 
    GetStaticticsHandler,
    MainPageHandler
)



def make_app(database: Database):
    # pass connection to each handler
    return tornado.web.Application([
        tornado.web.url(
            r'/api/add', RequestAddHandler, {'connection': database.connection()}, name='add'
        ),
        tornado.web.url(
            r'/api/get', RequestGetHandler, {'connection': database.connection()}, name='get'
        ),
        tornado.web.url(
            r'/api/remove', RequestDeleteHandler, {'connection': database.connection()}, name='delete'
        ),
        tornado.web.url(
            r'/api/update', RequestUpdateHandler, {'connection': database.connection()}, name='update'
        ),
        tornado.web.url(
            r'/api/statistic', GetStaticticsHandler, {'connection': database.connection()}, name='stats'
        ),
        tornado.web.url(
            r'/', tornado.web.RedirectHandler, {'url': '/api'}
        ),
        tornado.web.url(
            r'/api', MainPageHandler, name='main'
        ),
    ])


def main():
    # create database object and connect
    database = Database(os.getenv('DATABASE_URL'))
    IOLoop.current().run_sync(lambda: database.connect())
    # create app and run server
    app = make_app(database)
    server = HTTPServer(app)
    server.listen(os.getenv('APP_PORT'), address=os.getenv('APP_HOST'))
    print(f"The server is up and running at {os.getenv('APP_HOST')}:{os.getenv('APP_PORT')}")
    IOLoop.current().start()


if __name__ == '__main__':
    main()