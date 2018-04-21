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
            # Increment the score by one of this dish
            cmd = 'UPDATE Dish SET score = score + 1 WHERE name = %s AND RIN = %s;'
            cur.execute(cmd, [name, RIN])
            db.commit()
            return

        # Get a single restaurant
        if(params['request_type'][0] == 'find_restaurant'):
            RIN = params['RIN'][0]
            cmd = 'SELECT * FROM Restaurant WHERE RIN = %s;'
            cur.execute(cmd,RIN)
            data_from_db = cur.fetchall()
            self.wfile.write(bytes(json.dumps(data_from_db), "utf8"))
            return

        # Like button
        if(params['request_type'][0] == 'like_dish'):
            name = params['name'][0]
            RIN = params['RIN'][0]
            cmd = 'UPDATE Dish SET num_like = num_like + 1, score = score + 10 WHERE name = %s AND RIN = %s'
            cur.execute(cmd, [name, RIN])
            db.commit()
            message = json.dumps({'Status': 'OK', 'Message': 'SUCCEED'})
            # Write content as utf-8 data
            self.wfile.write(bytes(message, "utf8"))
            return

        # Cancel button
        if(params['request_type'][0] == 'cancel_like_dish'):
            name = params['name'][0]
            RIN = params['RIN'][0]
            cmd = 'UPDATE Dish SET num_like = num_like - 1, score = score - 10 WHERE name = %s AND RIN = %s'
            cur.execute(cmd, [name, RIN])
            db.commit()
            message = json.dumps({'Status': 'OK', 'Message': 'SUCCEED'})
            # Write content as utf-8 data
            self.wfile.write(bytes(message, "utf8"))
            return

        # Get top dishes of this restaurant
        if(params['request_type'][0] == 'top_dishes'):
            RIN = params['RIN'][0]
            cmd = 'SELECT * FROM Dish WHERE RIN = %s ORDER BY score desc LIMIT 3;'
            cur.execute(cmd,RIN)
            data_from_db = cur.fetchall()
            self.wfile.write(bytes(json.dumps(data_from_db), "utf8"))
            return

        # Get top 51 dishes
        if(params['request_type'][0] == 'top_51'):
            cmd = 'SELECT d.name, d.img, d.num_like, r.name, r.RIN FROM Dish d, Restaurant r WHERE d.RIN = r.RIN ORDER BY d.score desc LIMIT 51;'
            cur.execute(cmd)
            data_from_db = cur.fetchall()
            self.wfile.write(bytes(json.dumps(data_from_db),"utf8"))
            return

        if(params['request_type'][0] == 'search'):
            keyword = params['keyword'][0]
            keyword = '%' + keyword + '%'
            cmd = 'SELECT d.name, d.img, d.score, r.name, r.RIN FROM Dish d, Restaurant r WHERE d.RIN = r.RIN AND (d.name LIKE %s OR r.name LIKE %s OR d.description LIKE %s OR d.ingredient LIKE %s OR d.category LIKE %s OR r.category LIKE %s) ORDER BY d.score desc LIMIT 50'
            cur.execute(cmd,[keyword, keyword, keyword, keyword, keyword, keyword])
            data_from_db = cur.fetchall()
            self.wfile.write(bytes(json.dumps(data_from_db),"utf8"))
            return

        # Delete an entry from the database
        if(params['request_type'][0] == 'delete'):
            name = params['name'][0]
            RIN = params['RIN'][0]
            cmd = 'DELETE FROM Dish WHERE name = %s AND RIN = %s';
            cur.execute(cmd, [name, RIN])
            data_from_db = cur.fetchall()
            db.commit()
            self.wfile.write(bytes(json.dumps({'Status': 'OK'}),"utf8"))
            return

        # Query user history
        if(params['request_type'][0] == 'get_user_history'):
            user_name = params['user_name'][0]
            cmd = "SELECT GROUP_CONCAT(Dish.name SEPARATOR ',') AS dish_names, GROUP_CONCAT(Dish.img SEPARATOR ',') AS dish_images, SUM(Dish.calorie) AS total_calorie, History.User AS user FROM Dish, History where History.DIN = Dish.DIN AND History.User = %s group by History.date ORDER BY History.date"
            cur.execute(cmd, user_name)
            data_from_db = cur.fetchall()
            self.wfile.write(bytes(json.dumps(data_from_db),"utf8"))
            return


        # Send message back to client
        message = json.dumps(["hello",{"message": "world"}])
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

    # POST
    def do_POST(self):

        # Parse data
        length = int(self.headers.get('content-length'))
        field_data = self.rfile.read(length)
        params = parse_qs(field_data)
        print(params)


        if (b'request_type' not in params):
            return

        # send the headers
        self._set_headers()

        # Handle comment upload case
        if(params[b'request_type'][0] == b'comment_upload'):
            comment = params[b'content'][0].decode()
            User = params[b'user'][0].decode()
            dish = params[b'dish'][0].decode()
            RIN =  params[b'RIN'][0].decode()
            cmd = "INSERT INTO History (date, comment, DIN, User) VALUES ((SELECT NOW()), %s, (SELECT DIN FROM Dish WHERE name=%s AND RIN=%s), %s);"
            print(cmd%(comment, dish, RIN, User))
            cur.execute(cmd, [comment, dish, RIN, User])
            db.commit()
            message = json.dumps({'Status': 'OK', 'Message': 'SUCCEED'})
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
