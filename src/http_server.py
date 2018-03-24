from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import pymysql as mysql
import json
from credential import *
# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # Send header
    def _set_headers(self):
        self.send_response(200, 'OK')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Content-type','text/json')
        self.end_headers()

    # GET
    def do_GET(self):

        params = parse_qs(urlparse(self.path).query)
        print(params)

        if ('request_type' not in params):
            return
        # send the headers
        self._set_headers()

        # Get a single dish
        if(params['request_type'][0] == 'find_dish'):
            name = params['name'][0]
            RIN = params['RIN'][0]
            cmd = 'SELECT * FROM Dish WHERE name = %s AND RIN = %s;'
            cur.execute(cmd,[name, RIN])
            data_from_db = cur.fetchall()
            self.wfile.write(bytes(json.dumps(data_from_db), "utf8"))
            return

        # Get a single restaurant
        if(params['request_type'][0] == 'find_restaurant'):
            RIN = params['RIN'][0]
            cmd = 'SELECT * FROM Restaurant WHERE RIN = %s;'
            cur.execute(cmd,RIN)
            data_from_db = cur.fetchall()
            self.wfile.write(bytes(json.dumps(data_from_db), "utf8"))
            return

        # Get a single restaurant
        if(params['request_type'][0] == 'top_dishes'):
            RIN = params['RIN'][0]
            cmd = 'SELECT * FROM Dish WHERE RIN = %s ORDER BY score LIMIT 3;'
            cur.execute(cmd,RIN)
            data_from_db = cur.fetchall()
            self.wfile.write(bytes(json.dumps(data_from_db), "utf8"))
            return

        # Send message back to client
        message = json.dumps(["hello",{"message": "world"}])
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

    # POST
    def do_POST(self):

        self._set_headers()
        # Parse data
        length = int(self.headers.get('content-length'))
        field_data = self.rfile.read(length)
        fields = parse_qs(field_data)
        print(fields)

        message = json.dumps(["hello",{"message": "world"}])
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return


def run():
    print('starting server...')

    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('', 8081)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()

def connect_to_db():
    # Connect to the database
    connection = None
    print('Establishing database connection ...')
    connection = mysql.connect(host='localhost',
                             user=DB['username'],
                             password=DB['password'],
                             db=DB['database'],
                             charset='utf8',
                             cursorclass=mysql.cursors.DictCursor)


    return connection

if __name__ == "__main__":
    db = connect_to_db()
    cur = db.cursor()
    run()
