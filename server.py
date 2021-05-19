''' 
    Authors: Jacky Huynh & Jordan Cheung

    This file starts a TCP server to connect clients together, allowing them to send private messages to one another.
    The server has 2 threads that run in parrellel, one listening for new client connections, and one listening for client messages.
    When a new client connects to the server, the server will create a connection, and save the client connection to a array.
    When the server receives data from any client it sends the message to all clients saved inside the connections array.
    The server is only able to read the header of the data, it cannot read the message being sent.

    References used: 
        https://stackoverflow.com/questions/2719017/how-to-set-timeout-on-pythons-socket-recv-method
'''
import sys
import socket
import threading
import select
import time
from message_structure import send_message_structure
from message_structure import receive_message_structure


connections = []

# function that listens for new client connections
def listening_new_clients(s):
    
    # Keep on looping to receive connections
    print("SERVER IS LISTENING FOR CONNECTIONS")
    while (True):

        # Socket starts listening 
        s.listen(5)

        # accept the connection
        conn, addr = s.accept()
        conn.setblocking(0)

        # Add the connection to the list of connections
        connections.append(conn)
        print(addr, "connected" )

# function that listens for incoming data from clients. When data is received the server sends
# out the message to all other clients connected to the server
# the server can only read the header of the data, it reads the header to check if a client is disconnecting from the server
def listening_msg():

    while (True):
        # Loop through connections to see if there is a message to receive from the connection
        for current_conn_1 in connections:
            ready = select.select([current_conn_1], [], [], 0.01)
            if ready[0]:

                # Receive the message from the connection
                msg = current_conn_1.recv(4096)
                
                # Create a receive message structure
                recv_msg = receive_message_structure(msg)
                
                # If close flag is true close the connection and remove the connection from the connection list
                if(recv_msg.close_flag == 1):
                    print("CLIENT DISCONNECTED")
                    
                    # Close the connection with the client
                    current_conn_1.close()

                    # Remove the connection from the connection list
                    connections.remove(current_conn_1)

                    if(connections == []):
                        return
                        
                    # For connections that are in the list, send the final message that the client that disconnected sent
                    for current_conn_2 in connections:
                        if(current_conn_1 != current_conn_2):
                            current_conn_2.sendall(msg)
                # send messages to all other clients connected to the server
                else:
                    for current_conn_2 in connections:
                        if(current_conn_1 != current_conn_2):
                            current_conn_2.sendall(msg)
                        
def main(server_ip, server_socket):

    global connections

    # Create the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket
    s.bind((server_ip, server_socket))
    
    # Create the threads
    sending_thread = threading.Thread(target=listening_new_clients, args=(s,))
    listening_thread = threading.Thread(target=listening_msg)

    print("SERVER HAS STARTED")
    
    # Start sending and listening thread
    sending_thread.start()
    listening_thread.start()
    # join threads when they finish
    sending_thread.join()
    listening_thread.join()
    # close the socket
    s.close()

if __name__=='__main__':
    server_ip = sys.argv[1]
    server_socket = sys.argv[2]
    main(server_ip, int(server_socket))