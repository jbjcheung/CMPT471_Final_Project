''' 
    Authors: Jacky Huynh & Jordan Cheung

    This file contains structures that are used to create send and receive messages. The structures contain the neccessary methods
    to perform encoding, and decoding of the messages
    
    The message structure is in this form
        [close-flag] [key-flag] [length-of-message] [[nonce][tag][encrypted-message]]

    close_flag - is used to let the server, and other clients know that a client wants to disconnect from the chat server
    key_flag - is used to indicate that the message is used for the key-exchange
    message - contains the clients message
'''


from ecpy.curves import Curve, Point

# Get the curve
cv = Curve.get_curve('Curve25519')

# Class for sending messages
class send_message_structure:

    def __init__(self, msg, close_flag, key_flag):

        # Set self.close_flag to close_flag
        self.close_flag = close_flag
        
        # Set self.key_flag to key_flag
        self.key_flag = key_flag
        
        # Set self.message to msg
        self.message = msg

        # Check if the message is a key exchange message
        if (self.key_flag == 1):            
            # If the message is a key exchange, set the length to 32
            self.length = 32
        else:

            # Else set length to the length of the message
            self.length = len(self.message)

    def encode_data(self):
        
        # Convert the header fields to bytes
        close_flag_bytes = (self.close_flag).to_bytes(1, 'big')
        key_flag_bytes = (self.key_flag).to_bytes(1, 'big')
        length_bytes = (self.length).to_bytes(4, 'big')

        # Check if the message is a key exchange flag
        if(self.key_flag == 0):
            
            # The message is not a key exchange, just set message bytes to the message
            message_bytes = self.message
        else:
            # The message is a key exchange, the message is a point that needs to be encoded
            message_bytes = cv.encode_point(self.message)

        # Return the byte array of format [close-flag] [key-flag] [length-of-message] [msg]
        return ( close_flag_bytes + key_flag_bytes + length_bytes + message_bytes )

class receive_message_structure:

    # header length is 6 b/c
    # close_flag - 1 byte
    # key_flag - 1 byte
    # length - 4 bytes
    # 1 byte + 1 byte + 4 byte = 6 bytes
    
    header_length = 6

    def __init__(self, msg):
        
        # Set the member variables to the appropriate decoded message
        self.length = self.decode_length(msg)
        self.close_flag = self.decode_close_flag(msg)
        self.key_flag = self.decode_key_flag(msg)
        self.msg = self.decode_msg(msg, self.length)

    # Decode Length 
    def decode_length(self, data):
        
        # Get the bytes from the length field
        length_bytes = data[2:self.header_length]

        # Convert from bytes to int
        actual_length = int.from_bytes(length_bytes, byteorder="big", signed = 'false')
        return actual_length

    def decode_close_flag(self, data):

        # Get the bytes from the close flag field
        close_bytes = data[0:1]

        # Convert from bytes to int
        close = int.from_bytes(close_bytes, byteorder="big", signed = 'false')

        return close

    def decode_key_flag(self, data):
        
        # Get the key exchange flag
        key_bytes = data[1:2]

        # Convert the bytes to int
        key = int.from_bytes(key_bytes, byteorder="big", signed = 'false')
        return key
        
    def decode_msg(self, data, num_bytes):

        # Checks if it's a key exchange
        if (self.key_flag == False):
            # Return the bytes from header length to the end of the message
            return data[self.header_length:self.header_length+num_bytes+1]
        else:
            # Return the bytes from header length to the end of the message and decode the point
            return cv.decode_point(data[self.header_length:self.header_length+num_bytes+1])