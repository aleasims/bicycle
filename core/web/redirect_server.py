from http.server import SimpleHTTPRequestHandler, HTTPServer 
import sys
import argparse    

class RedirectHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(301)
        self.send_header('Location', self.redirect_url)
        self.end_headers()

class RedirectServer():
    def __init__(self, config, logger):
        super().__init__()
        self.logger = logger
        self.config = config
        self.host, self.second_port, domain = config['host'], config['second_port'], config['domain']
        RedirectHandler.redirect_url = 'https://' + domain
        self.server = HTTPServer((self.host, self.second_port), RedirectHandler)

    def start(self):
        self.logger.info('Starting server on {}'.format(self.second_port))
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Server stopping')
