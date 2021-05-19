''' 
    Authors: Jacky Huynh & Jordan Cheung
    
    This file contains the neccessary functions to generate the keys for Elliptic-curve Diffie–Hellman Key Exchange

    References used: 
        https://en.wikipedia.org/wiki/Signal_Protocol
        https://en.wikipedia.org/wiki/Elliptic-curve_Diffie%E2%80%93Hellman#:~:text=Elliptic%2Dcurve%20Diffie%E2%80%93Hellman%20(,secret%20over%20an%20insecure%20channel.&text=The%20key%2C%20or%20the%20derived,using%20a%20symmetric%2Dkey%20cipher.
'''

import random
from ecpy.curves import Curve, Point
import math
import secrets

# Get the curve for Curve25519
cv = Curve.get_curve('Curve25519')

# Generate private key
def generate_private_key():

    # Get a random point on the elliptic curve
    return secrets.randbelow(cv.field) 

# Generate public key from private key
def generate_public_key(private_key):

    # Multiply the private key with a point on the elliptic curve
    return private_key * cv.generator

# Generate shared key
def generate_shared_key(private_key, public_key):

    # Multiply the private key and the public key
    return private_key * public_key