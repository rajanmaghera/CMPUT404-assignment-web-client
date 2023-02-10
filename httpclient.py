#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2023 Rajan Maghera
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def get_request(url, host, args=None):
    """Return a GET request body with headers"""

    # we want to add the args to the url

    # if there is a ? in the url, the separator is &
    # else, the separator is ?
    if "?" in url:
        separator = "&"
    else:
        separator = "?"

    encoded_args = separator + urllib.parse.urlencode(args) if args != None else ""

    return f"""GET {url}{encoded_args} HTTP/1.1\r
Host: {host}\r
Connection: close\r
\r
"""

def post_request(url, host, args=None):
    """Return a POST request body with headers"""

    encoded_args = urllib.parse.urlencode(args) if args != None else ""

    return f"""POST {url} HTTP/1.1\r
Host: {host}\r
Connection: close\r
Content-Type: application/x-www-form-urlencoded\r
Content-Length: {len(encoded_args)}\r
\r
{encoded_args}"""

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return f"Code: {self.code}\r\n--- Body --- \r\n{self.body}"

class HTTPClient(object):

    def request(self, url, method="GET", args=None):
        """Send HTTP request and return HTTP response"""

        # parse the url
        self.get_host_port(url)
        self.get_url_params(url)

        # connect to the server
        self.connect(self.host, self.port)

        # send the request based on the method
        if method == "GET":
            req = get_request(self.url, self.host, args)
        elif method == "POST":
            req = post_request(self.url, self.host, args)
        else:
            return None

        # send the request
        self.socket.sendall(req.encode())

        # receive the response
        data = self.recvall(self.socket)
        self.close()

        # return the response
        return HTTPResponse(self.get_code(data), self.get_body(data))

    def get_url_params(self, url):
        """Add the query params back to the url"""

        # parse the url
        parsed = urllib.parse.urlparse(url)

        # append query params back to url
        if parsed.query != "":
            self.url = parsed.path + "?" + parsed.query

    def get_host_port(self,url):
        """Parse the url and return the host and port"""

        # parse the url
        parsed = urllib.parse.urlparse(url)

        # store attributes
        self.host = parsed.hostname
        self.port = parsed.port
        self.url = parsed.path

        # determine a port if none is provided
        if parsed.scheme == "https" and self.port == None:
            self.port = 443
        elif parsed.scheme == "http" and self.port == None:
            self.port = 80


        # determine a url if none is provided
        if self.port == None:
            self.port = 80

        if self.url == "":
            self.url = "/"


    def connect(self, host, port):
        """Connect to the server via sockets"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        """Return the response code"""
        data = data.split(" ")
        return int(data[1])

    def get_body(self, data):
        """Return the response body"""
        return data.split("\r\n\r\n")[1]

    def sendall(self, data):
        """Send all data to the server"""
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        """Close the socket"""
        self.socket.close()

    def recvall(self, sock):
        """Read everything from the socket"""
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        """Execute a GET request"""
        return self.request(url, "GET", args)

    def POST(self, url, args=None):
        """Execute a POST request"""
        return self.request(url, "POST", args)

    def command(self, url, command="GET", args=None):
        """Parse a command and execute it"""
        return self.request(url, command, args)

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
