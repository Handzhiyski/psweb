#!/usr/bin/env python3

import logging
import tornado.ioloop
import tornado.web
import psutil
import argparse
import subprocess

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('psweb_debug.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)

parser = argparse.ArgumentParser()
parser.add_argument("-ip", "--ip_address", type=str, help="Specify ip address", default='127.0.0.1')
parser.add_argument("-p", "--port", type=int, help="Specify port number", default=5000)
parser.add_argument('params', metavar='param', type=str, nargs='*', help='params')

args = parser.parse_args()


class GetRequestHandler(tornado.web.RequestHandler):

    def get(self):

        system_stats = {
            "cpu_prc": (psutil.cpu_percent()),
            "free_memory_mb": round((psutil.virtual_memory()[1])/1024**2)
        }

        self.write(system_stats)


class PostRequestHandler(tornado.web.RequestHandler):

    def post(self):

        body = self.request.body
        logger.info("command to run: {}".format(body))
        self.set_header("Content-Type", "application/text")

        command_line = body
        command_line = command_line.split()

        try:
            p = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = p.communicate()
            logger.debug(output[0].decode('utf-8'))
            self.write(output[0])

        except OSError as e:
            print(e)
            logger.exception(e)
            self.set_status(400, str(e))


def make_app():
    return tornado.web.Application([
        (r"/load", GetRequestHandler),
        (r"/cmd", PostRequestHandler),
    ])


if __name__ == "__main__":

    app = make_app()

    logger.info("Server running on {}:{}".format(args.ip_address, args.port))

    app.listen(args.port, address=args.ip_address)
    tornado.ioloop.IOLoop.current().start()
