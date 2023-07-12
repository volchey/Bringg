from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from fedex import FedEx, RequestException

class RequestHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        # Set response headers for CORS preflight request
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()


    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        # Extract the input value from the request data
        input_value = data.get('input')

        # Perform any necessary processing or calculations with the input value
        fedex = FedEx()
        try:
            fedex.auth()
            # print(fedex.barear)
            result = fedex.track(input_value)
            # print(json.dumps(result))
        except RequestException as e:
            print(e)
            return


        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header("Access-Control-Allow-Origin", '*')
        self.end_headers()

        # Send the response
        # self.wfile.write(result)
        self.wfile.write(json.dumps(result).encode('utf-8'))
        print(json.dumps(result).encode('utf-8'))


def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
