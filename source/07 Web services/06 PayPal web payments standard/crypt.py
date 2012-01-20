#!/usr/bin/env python
# coding: utf8
from gluon import *

from M2Crypto import BIO, SMIME, X509, EVP

def paypal_encrypt(attributes, sitesettings):
    """
    Takes a list of attributes for working with PayPal (in our case adding to
    the shopping cart), and encrypts them for secure transmission of item
    details and prices.

    @type  attributes: dictionary
    @param attributes: a dictionary of the PayPal request attributes.  An
      example attribute set is:

      >>> attributes = {"cert_id":sitesettings.paypal_cert_id,
                        "cmd":"_cart",
                        "business":sitesettings.cart_business,
                        "add":"1",
                        "custom":auth.user.id,
                        "item_name":"song 1 test",
                        "item_number":"song-1",
                        "amount":"0.99",
                        "currency_code":"USD",
                        "shopping_url":'http://'+\
                           Storage(globals()).request.env.http_host+\
                           URL(args=request.args),
                        "return":'http://'+\
                           Storage(globals()).request.env.http_host+\
                           URL('account', 'downloads'),
                        }

    @type  sitesettings: SQLStorage
    @param sitesettings: The settings stored in the database.  this method
      requires I{tenthrow_private_key}, I{tenthrow_public_cert}, and
      I{paypal_public_cert} to function
    @rtype: string
    @return: encrupted attribute string
    """

    plaintext = ''

    for key, value in attributes.items():
        plaintext += u'%s=%s\n' % (key, value)

    plaintext = plaintext.encode('utf-8')

    # Instantiate an SMIME object.
    s = SMIME.SMIME()

    # Load signer's key and cert. Sign the buffer.
    s.pkey = EVP.load_key_string(sitesettings.tenthrow_private_key)
    s.x509 = X509.load_cert_string(sitesettings.tenthrow_public_cert)

    #s.load_key_bio(BIO.openfile(settings.MY_KEYPAIR),
    #               BIO.openfile(settings.MY_CERT))

    p7 = s.sign(BIO.MemoryBuffer(plaintext), flags=SMIME.PKCS7_BINARY)

    # Load target cert to encrypt the signed message to.
    #x509 = X509.load_cert_bio(BIO.openfile(settings.PAYPAL_CERT))
    x509 = X509.load_cert_string(sitesettings.paypal_public_cert)

    sk = X509.X509_Stack()
    sk.push(x509)
    s.set_x509_stack(sk)

    # Set cipher: 3-key triple-DES in CBC mode.
    s.set_cipher(SMIME.Cipher('des_ede3_cbc'))

    # Create a temporary buffer.
    tmp = BIO.MemoryBuffer()

    # Write the signed message into the temporary buffer.
    p7.write_der(tmp)

    # Encrypt the temporary buffer.
    p7 = s.encrypt(tmp, flags=SMIME.PKCS7_BINARY)

    # Output p7 in mail-friendly format.
    out = BIO.MemoryBuffer()
    p7.write(out)

    return out.read()
