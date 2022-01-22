import os
import os.path
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from dotenv import load_dotenv



def make_app():
    return tornado.web.Application([
        
    ])


def main():
    load_dotenv()
    app = make_app()
    server = HTTPServer(app)
    server.listen(os.getenv('APP_PORT'), address=os.getenv('APP_HOST'))
    print(f"The server is up and running at {os.getenv('APP_HOST')}:{os.getenv('APP_PORT')}")
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()