import socket
import os
import datetime
import signal
import sys
import selectors

BUFFER_SIZE = 2048
sel = selectors.DefaultSelector()

class user:
    def __init__(self, username, address, socket): 
        self.username = username
        self.address = address
        self.socket = socket

# Handles Ctrl + C exiting smoothly

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')

    for u in users:
        u.socket.send('DISCONNECT CHAT/1.0'.encode())
        u.socket.close()
    sys.exit(0)

# Removes victim from the list of users

def remove_user(victim, users):
    for u in users:
        if u.username == victim:
            users.remove(u) 
            break

# Checks if a user is already registered, returns true if they are

def check_username(username, users):

    for u in users:
        if u.username == username:
            return True
    return False

# Accepts connection from a client socket and registers it

def accept(sock, mask, users):

    # Attempt a connection 

    try:
        conn, addr = sock.accept() 
    except i as InterruptedError:
        print('400 Invalid Registration')
        conn.send('400 Invalid Registration'.encode())
        exit(1)
    print('Accepted connection from client address:', addr)

    # Receive username + register the socket

    username = conn.recv(BUFFER_SIZE).decode()
    conn.setblocking(False)

    if check_username(username, users):
        print('401 Client already registered')
        conn.send('401 Client already registered'.encode())
    else:
        print('200 Registration successful')
        conn.send('200 Registration successful'.encode())
        print('Connection established. Welcome ' + repr(username))
        users.append(user(username, addr, conn))

        sel.register(conn, selectors.EVENT_READ, read)
        print('Register', username, 'CHAT/1.0')

# Receive a message from a client and broadcast to others

def read(conn, mask, users):
    msg = conn.recv(BUFFER_SIZE)

    # Find out which user sent the message

    sender_addr = conn.getpeername()
    for u in users:
        if u.address == sender_addr:
            username = u.username
            address = u.address
            break

    # Save disconnection msg for potential disconnection

    disc_msg = 'DISCONNECT ' + username + ' CHAT/1.0' 

    if msg: # If message exists

        print('Received message from:', username, repr(msg.decode()))

        if (msg.decode() == disc_msg): # If message is to disconnect
            print('Disconnecting', username)
            sel.unregister(conn)
            remove_user(username, users)
            conn.close()
        else:
            for u in users:
                if username != u.username:
                    u.socket.send(msg)

    else:
        print('Disconnecting', username)
        sel.unregister(conn)
        remove_user(username, users)
        conn.close()

# Main function

def main():
    global users # Global list that holds all current users
    users = []

    # Create our signal handler for shutting down (Ctrl+C).

    signal.signal(signal.SIGINT, signal_handler)

    # Create socket, pick a random free port, and print the port for 
    # clients.

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 0))

    # Begin listening for connections from clients

    server_socket.listen(20)
    print('Will wait for client messages at port ' + str(server_socket.getsockname()[1]))
    print('Waiting for incoming client connections..')

    # Register server socket to monitor any connections.

    sel.register(server_socket, selectors.EVENT_READ, accept)

     # Keep the server running forever.

    while(1):

        # Monitor for activity in the server socket so we can accept

        events = sel.select()

        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask, users)
 
if __name__ == '__main__':
    main()
