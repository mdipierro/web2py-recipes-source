# coding: utf8
# intente algo como
def index(): return dict(message="hello from paypal.py")

from applications.paypal_payments.modules.openanything import *

def ipn():
    """
    This controller processes Instant Payment Notifications from PayPal.

    It will verify messages, and process completed cart transaction messages
    only.  all other messages are ignored for now.

    For each item purchased in the cart, the song_purchases table will be
    updated with the purchased item information, allowing the user to
    download the item.

    logs are written to /tmp/ipnresp.txt

    the PayPal IPN documentation is available at:
    https://cms.paypal.com/cms_content/US/en_US/files/developer/IPNGuide.pdf
    """
    """
    sample PayPal IPN call:

    last_name=Smith&
    txn_id=597202352&
    receiver_email=seller%40paypalsandbox.com&
    payment_status=Completed&tax=2.02&
    mc_gross1=12.34&
    payer_status=verified&
    residence_country=US&
    invoice=abc1234&
    item_name1=something&
    txn_type=cart&
    item_number1=201&
    quantity1=1&
    payment_date=16%3A52%3A59+Jul.+20%2C+2009+PDT&
    first_name=John&
    mc_shipping=3.02&
    charset=windows-1252&
    custom=3&
    notify_version=2.4&
    test_ipn=1&
    receiver_id=TESTSELLERID1&
    business=seller%40paypalsandbox.com&
    mc_handling1=1.67&
    payer_id=TESTBUYERID01&
    verify_sign=AFcWxV21C7fd0v3bYYYRCpSSRl31AtrKNnsnrW3-8M8R-P38QFsqBaQM&
    mc_handling=2.06&
    mc_fee=0.44&
    mc_currency=USD&
    payer_email=buyer%40paypalsandbox.com&
    payment_type=instant&
    mc_gross=15.34&
    mc_shipping1=1.02
    """

    #@todo: come up with better logging mechanism
    logfile = "/tmp/ipnresp.txt"

    verifyurl = "https://www.paypal.com/cgi-bin/webscr"
    if request.vars.test_ipn != None and request.vars.test_ipn == '1':
        verifyurl = "https://www.sandbox.paypal.com/cgi-bin/webscr"

    params = dict(request.vars)
    params['cmd'] = '_notify-validate'

    resp = fetch(verifyurl, post_data=params)

    #the message was not verified, fail
    if resp['data'] != "VERIFIED":
        #@todo: figure out how to fail
        f = open(logfile, "a")
        f.write("Message not verified:\n")
        f.write(repr(params) + "\n\n")
        f.close()
        return None

    #check transaction type
    #@todo: deal with types that are not cart checkout
    if request.vars.txn_type != "cart":
        #for now ignore non-cart transaction messages
        f = open(logfile, "a")
        f.write("Not a cart message:\n")
        f.write(repr(params) + "\n\n")
        f.close()
        return None

    #@TODO: check that payment_status == Completed
    if request.vars.payment_status != 'Completed':
        #ignore pending transactions
        f = open(logfile, "a")
        f.write("Ignore pending transaction:\n")
        f.write(repr(params) + "\n\n")
        f.close()
        return None

    #check id not recorded
    if len(db(db.song_purchases.transaction_id==request.vars.txn_id).select())>0:
        #transaction already recorded
        f = open(logfile, "a")
        f.write("Ignoring recorded transaction:\n")
        f.write(repr(params) + "\n\n")
        f.close()
        return None

    #record transaction
    num_items = 1
    if request.vars.num_cart_items != None:
        num_items = request.vars.num_cart_items

    for i in range(1, int(num_items)+1):
        #i coded our item_number to be a tag and an ID.  the ID is
        # a key to a table in our database.
        tag, id = request.vars['item_number'+str(i)].split("-")
        if tag == "song":
            db.song_purchases.insert(auth_user=request.vars.custom,
                           cue_point=id,
                           transaction_id=request.vars.txn_id,
                           date=request.vars.payment_date.replace('.', ''))
        elif tag == "song_media":
            db.song_purchases.insert(auth_user=request.vars.custom,
                           song_media=id,
                           transaction_id=request.vars.txn_id,
                           date=request.vars.payment_date.replace('.', ''))
        elif tag == "concert":
            db.concert_purchases.insert(auth_user=request.vars.custom,
                              playlist=id,
                              transaction_id=request.vars.txn_id,
                              date=request.vars.payment_date.replace('.', ''))
        else:
            #@TODO: this is an error, what should we do here?
            f = open(logfile, "a")
            f.write("Ignoring bad item number: " + \
                        request.vars['item_number'+str(i)] + "\n")
            f.write(repr(params) + "\n\n")
            f.close()

    f = open(logfile, "a")
    f.write("Processed message:\n")
    f.write(repr(params) + "\n\n")
    f.close()
    return None
