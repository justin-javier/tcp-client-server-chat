import socket
import os
import selectors
import argparse
import signal
from urllib.parse import urlparse
import sys

# Define a constant for our buffer size

BUFFER_SIZE = 2048
sel = selectors.DefaultSelector()

# Handle if user leaves with Ctrl + C

def signal_handler(sig, frame):

    print('Interrupt received, shutting down ...')
    disc_msg = 'DISCONNECT ' + username + ' CHAT/1.0' 
    client_socket.send(disc_msg.encode())
    sys.exit(0)

# Function records both host name and server URL 

def parseInput():

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Host name of server")
    parser.add_argument("url", help="URL of server")
    args = parser.parse_args()
    return args

# Function takes input and writes to the socket

def send():
    msg = sys.stdin.readline()
    msg = ('@' + username + ': ' + msg).rstrip()
    client_socket.send(msg.encode())
    sys.stdout.flush()

# Function receives message from server, performs checks, and prints

def receive():
    msg = client_socket.recv(BUFFER_SIZE).decode()
    if msg == '401 Client already registered':
        print('401 Client already registered')
        sys.exit(0)
    elif msg == '400 Invalid Registration':
        print('400 Invalid Registration')
        sys.exit(0)
    elif msg == 'DISCONNECT CHAT/1.0':
        print('Server terminated.. Exiting now')
        sys.exit(0)
    else:
        print(msg)

# Our main function.

def main():

    # Socket and username made available to the whole program

    global client_socket
    global username

    # Check command line arguments to get the username and URL.

    args = parseInput();
    username = args.name

    # Parse through the URL to get necessary information 

    url = urlparse(args.url)

    # Now we try to make a connection to the server.

    print('Connecting to server ...')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        client_socket.connect((url.hostname,url.port))
        client_socket.send(username.encode())
        client_socket.setblocking(False)

    except TimeoutError as e:
        print('Failed to establish connection. Closing ...')
        exit(1)

    # Register the client socket to monitor any events to be 
    # read or to be written

    sel.register(client_socket, selectors.EVENT_READ)
    sel.register(sys.stdin, selectors.EVENT_READ)

    print('Connection established.')
    print('Registration successful! Welcome ' + username)

    while(1):

        # Wait for a selector registered event

        events = sel.select()

        for key, mask in events:
            if key.fileobj == client_socket:
                receive()
            else:
                send()

    client_socket.close()

if __name__ == '__main__':
    main()