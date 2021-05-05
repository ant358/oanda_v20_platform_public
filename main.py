# %%
import os
import sys
import time
import schedule
import importlib
import subprocess
from datetime import datetime
from setup.args import parse_args
from notifier.sms import TwilioSMS
from notifier.email import send_email_notification
from utils.hardware_usage import check_sys_usage

from io import StringIO

# import account details
from auth.auth import Tokens
t = Tokens()

# import config ini 
import configparser
config = configparser.ConfigParser()
config.read('setup/config.ini')
# %%
########## set up logging ###########################
import logging
# get todays date
datestamp = datetime.now().strftime('%Y%m%d')

# use append date to logfile name
log_name = f'log-{datestamp}.txt'
path = './logs/'
log_filename = os.path.join(path, log_name)

# create log if it does not exist
if not os.path.exists(log_filename):
        open(log_filename, 'w').close()

# create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# Set up the file handler
file_logger = logging.FileHandler(log_filename)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('[%(levelname)s] - %(asctime)s - %(name)s : %(message)s')
# add formatter
file_logger.setFormatter(formatter)
ch.setFormatter(formatter)
# add a handler to logger
logger.addHandler(file_logger)
logger.addHandler(ch)
# mark the run
logger.info('Program Started')

####################################################################################
# %%
def run_strategy():
    args = parse_args()

    # SETS UP BROKER CONFIGURATIONS:
    systemkwargs = dict(
        token              = t.token, 
        account            = t.account,
        practice           = config.getboolean('Account', 'practice', fallback=False), 
        pair               = args.pair, 
        backfill           = config.getboolean('Trading', 'backfill', fallback=True),
        text_notifications = config.getboolean('Twilio', 
                            'text_notifications', fallback=False), 
        recipient_number   = config.getint('Twilio', 'recipient_number', fallback=None),
        twilio_number      = config.getint('Twilio', 
                            'twilio_number', fallback=None),
        twilio_sid         = config.get('Twilio', 
                             'twilio_sid', fallback=None),
        twilio_token       = config.get('Twilio', 
                             'twilio_token', fallback=None),
                        )

    # IMPORTS THE TRADING STRATEGY DYNAMICALLY BASED UPON THE ROBOT FILE NAME PASSED IN THE ARGS
    bot_system = getattr(importlib.import_module('strategies'), args.bot)
    # from strategies  import price_printer
    #from strategies import rsi_test
    # from strategies import simple_order_test

    # SETS THE BOT TRADING STRATEGY TO RUN WITH OANDA:
    # strategy = price_printer.price_printer(oanda)
    strategy = bot_system(**systemkwargs)
    # strategy = simple_order_test.simple_order_test(oanda)

    # PREPARES AND BUNDLES THE TRADING ACTION JOBS FOR EXECUTION (GET DATA / RUN STRATEGY):
    
    def job():
        # For localhost hardware performance testing - DigitalOcean does this natively
        # check_sys_usage()   
        first_data_object = strategy.data0[0]
        strategy.refresh_data()
        updated_first_data_object = strategy.data0[0]
        if first_data_object != updated_first_data_object:
            strategy.__next__()


    # SETS SCHEDULER TO FETCH NEW DATA AND RUN STRATEGY INTERVALS:
    schedule.every(30).seconds.do(job)


    # KEEPS THE SYSTEM ONLINE INDEFINITELY WHILE MINIMIZING RESOURCE CONSUMPTION:
    while True:
        schedule.run_pending()
        # Comment this line out if you want to test server overloading and torture testing
        time.sleep(1) 
        

# INITIALIZES ROBOT AND SCRIPTS  
if __name__ == '__main__':
    try:
        args = parse_args()
        if config.get('Email', 'email_to', fallback=None):
            email_subject = f'Python Bot Stared --- {args.pair} --- {args.bot}' 
            email_body = 'System is online'
            send_email_notification(
                config.get('Email','gmail_server_account', fallback=None),
                config.get('Email','gmail_server_password', fallback=None),
                config.get('Email', 'email_to', fallback=None), 
                email_subject, 
                email_body
            )

        run_strategy()
        

# GRACEFUL EXIT ON PROGRAM CRASH WITH EMAIL NOTIFICATION OF FAILURE REASON
    except:
        logger.exception('Failed to run strategy')

    if config.get('Email', 'email_to', fallback=None):
        args = parse_args()
        log_stream = StringIO()
        email_subject = f'Python Bot STOPPED! --- {args.pair} --- {args.bot}'
        email_body = log_stream.getvalue()
        send_email_notification(
            config.get('Email','gmail_server_account', fallback=None),
            config.get('Email','gmail_server_password', fallback=None),
            config.get('Email', 'email_to', fallback=None),  
            email_subject, 
            email_body
        )
    logger.info('Run strategy finished')
# %%
