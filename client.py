''' 
    Authors: Jacky Huynh & Jordan Cheung
    
    This file starts a TCP connection to a server, 
    in which the client is then able to send messages to another client connected to the server.
    The client first starts off by doing a Elliptic-curve Diffie–Hellman Key Exchange. After the key exchange
    the client now shares a shared key that only clients know, they use this shared key to encrypt, and decrypt their
    messages before sending them out.

    References used: 
        https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html
        https://en.wikipedia.org/wiki/Signal_Protocol
'''

import sys
import socket
import threading
import select
from Crypto.Cipher import AES
from encryption import *
from message_structure import send_message_structure
from message_structure import receive_message_structure

shared_key = ''
username = ''
close_flag = False


# function to encrypt messages that are being sent out
def encrypt(msg):
    # Encode the msg to bytes to pass to encrypt and digest
    b_msg = msg.encode()
    
    # Convert the shared key to bytes
    shared_key_bytes = (shared_key).to_bytes(32, 'big')

    # Create the cipher
    AES_cipher = AES.new(shared_key_bytes, AES.MODE_EAX)
    nonce = AES_cipher.nonce

    # Get Ciphertext and tag 
    ciphertext, tag = AES_cipher.encrypt_and_digest(b_msg)

    # Return the nonce, tag and ciphertext as a combined bytes array
    return nonce + tag + ciphertext

# function to decrypt messages that are received
def decrypt(msg):

    # Get the shared key in bytes
    shared_key_bytes = (shared_key).to_bytes(32, 'big')

    # Get the nonce and tag from the received msg
    nonce = msg[:16]
    tag = msg[16:32]

    # Rebuild the cipher from what we received
    cipher = AES.new(shared_key_bytes, AES.MODE_EAX, nonce=nonce)

    # Decrypt the message 
    plaintext = cipher.decrypt(msg[32:])
    
    # Verify the message and return
    try:
        cipher.verify(tag)
        return plaintext.decode()
    except ValueError:
        return "DECRYPTION FAILED"

def sending_msg(s):

    # Loop to keep on receiving input
    while (True):
        
        # User inputs their message
        client_msg = input()

        # Check if the user wants to close the application
        if (client_msg == "close()"):
            
            # Set the close_flag to true
            global close_flag
            close_flag = 1
            
            # Send a message to the server that states that the client is closing
            encrypted_final_msg = encrypt(client_msg)
            # create a message object with the encrypted message, and with close flag to true
            send_msg = send_message_structure(encrypted_final_msg, True, False)
            # encode the data and send it out
            send_bytes = send_msg.encode_data()
            bytes_sent = s.send(send_bytes)
            return
        else:
            
            # Create the message
            final_msg = '\n' + username + ": " + client_msg

            # Encrypt the message
            encrypted_final_msg = encrypt(final_msg)
            
            # create a message object with the encrypted message, with close, and key flag to false
            send_msg = send_message_structure(encrypted_final_msg, False, False)
            send_bytes = send_msg.encode_data()
            bytes_sent = s.send(send_bytes)
                
# function that listens from incoming messages
def listening_msg(s):

    msg = ''

    # Loop to receive messages
    while (True):

        # Receive message from socket
        msg = s.recv(4096)
        recv_msg = receive_message_structure(msg)
        
        # If the close_flag is true stop listening by returning
        if (close_flag == True):
            return

        # The other client has disconnected, do a key exchange with a new incoming client
        if (recv_msg.close_flag == True):
            print("OTHER CLIENT DISCONNECTED")
            
            # Set the global variable shared_key to be the result of the key exchange
            global shared_key
            shared_key = key_exchange(s)
        else:
            # decrypt incoming message
            print(decrypt(recv_msg.msg))

    return
    
# Function that does the Diffie–Hellman Key Exchange
def key_exchange(s):

    # Generate the public and private keys
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)

    # Create the send message structure with the key flag on
    send_msg = send_message_structure(public_key, False, True)

    received_key_bytes = 0
    
    # continually keep sending out public key to other clients, until a reply is received
    while ( received_key_bytes == 0 ):
        s.send(send_msg.encode_data())
        ready = select.select([s], [], [], 0.01)
        if(ready[0]):
            # received another public key from another client
            received_key_bytes = s.recv(4096)
            
        if (close_flag == True):
            return

    # Put the received bytes into a receive message structure
    received_key_msg = receive_message_structure(received_key_bytes)

    # Get the message from the receive key structure
    received_key = received_key_msg.msg

    # Generate the shared key
    shared_key = generate_shared_key(private_key, received_key)

    # Return the x-axis of the shared key
    return shared_key.x

def main(server_ip, server_socket):
    
    # Set the username
    global username
    global close_flag
    username = input("What's your name?: ")
    
    # Makes sure the username is shorter than 16 characters
    while (len(username) > 16):
        username = input("Username must be less than 16 characters, please try again: ") 
        
    # connect to server
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, server_socket))
        print("Successfully connected to server!")
    except socket.error as err:
        print("Error in connecting to server!")

    # Sets the global shared key to the value from key exchange
    global shared_key
    shared_key = key_exchange(s)
    
    # Send a message to other the client that you have joined the room
    msg = '\n' + username + " has joined the chatroom!"
    encrypt_msg = encrypt(msg)
    send_msg = send_message_structure(encrypt_msg, False, False)
    send_bytes = send_msg.encode_data()
    bytes_sent = s.send(send_bytes)

    # creating threads, so client program can listen and send messages in parrallel
    sending_thread = threading.Thread(target=sending_msg, args=(s,))
    listening_thread = threading.Thread(target=listening_msg, args=(s,))
    # start the threads
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