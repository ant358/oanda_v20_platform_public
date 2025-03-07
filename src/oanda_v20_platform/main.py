# %%
# set up logging
import logging
from datetime import datetime
from oanda_v20_platform.data.marketdata import MarketData
from oanda_v20_platform.utils.fileops import get_abs_path
# %%
# get todays date
datestamp = datetime.now().strftime('%Y%m%d')

# append date to logfile name
log_name = f'log-{datestamp}.txt'
# path = './logs/'
log_filename = get_abs_path(['logs', log_name])
# print(log_filename)
# create log if it does not exist
if not log_filename.exists():
    # check the  logs dir exists - create it
    get_abs_path(['logs']).mkdir(exist_ok=True)
    # create the file
    log_filename.touch(exist_ok=True)


# create logger
logger = logging.getLogger()
# set minimum output level
logger.setLevel(logging.DEBUG)
# Set up the file handler
file_logger = logging.FileHandler(log_filename)

# create console handler and set level to debug
ch = logging.StreamHandler()
# set minimum output level
ch.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('[%(levelname)s] -'
                              ' %(asctime)s - '
                              '%(name)s : %(message)s')
# add formatter
file_logger.setFormatter(formatter)
ch.setFormatter(formatter)
# add a handler to logger
logger.addHandler(file_logger)
logger.addHandler(ch)
# mark the run
logger.info('Oanda_v20_platform Started')

##############################################################################

try:
    # import python modules and packages
    import importlib
    from io import StringIO
    from decouple import config
except Exception:
    logger.exception("Failed to import python modules,"
                     " is the environment correctly setup?")

try:
    # import local modules
    from oanda_v20_platform.config.args import parse_args
    from oanda_v20_platform.notifier.email import send_email_notification
except Exception:
    logger.exception("Failed to import local modules,"
                     " have the paths been changed?")

try:
    import configparser
    config_local = configparser.ConfigParser()
    config_local.read(get_abs_path(['config', 'config.ini']))
except Exception:
    logger.exception("Failed to import config file,"
                     " has it been moved or edited?")


def run_strategy():
    args = parse_args()
    # SETS UP BROKER CONFIGURATIONS:
    systemkwargs = dict(
        token=config('PRACTICE_TOKEN'),
        account=config('PRACTICE_ACCOUNT'),
        practice=config_local.getboolean('Account', 'practice',
                                         fallback=False),
        pair=args.pair,
        backfill=config_local.getboolean('Trading', 'backfill', fallback=True),
        text_notifications=config_local.getboolean('Twilio',
                                                   'text_notifications',
                                                   fallback=False),
        recipient_number=config_local.getint('Twilio',
                                             'recipient_number',
                                             fallback=None),
        twilio_number=config_local.getint('Twilio',
                                          'twilio_number', fallback=None),
        twilio_sid=config_local.get('Twilio',
                                    'twilio_sid', fallback=None),
        twilio_token=config_local.get('Twilio',
                                      'twilio_token', fallback=None),
                        )

    # IMPORTS THE TRADING STRATEGY DYNAMICALLY
    # BASED UPON THE ROBOT FILE NAME PASSED IN THE ARGS
    try:
        bot_system = \
            getattr(importlib.import_module('oanda_v20_platform.strategies'),
                    args.bot)
    except Exception:
        logger.exception('Failed to load bot, check its name is correct')

    # SETS THE BOT TRADING STRATEGY TO RUN WITH OANDA
    bot_system(**systemkwargs)


# INITIALIZES ROBOT AND SCRIPTS
if __name__ == '__main__':

    ###########################################################################
    # update market data
    try:
        # TODO schedule the rebuild of MarketData at the start of
        # each day e.g. 00:01
        md = MarketData()

    except Exception:
        logger.exception("Failed to update market data")

    try:
        args = parse_args()
        if config_local.get('Email', 'email_to', fallback=None):
            email_subject = f'Python Bot Stared --- {args.pair} --- {args.bot}'
            email_body = 'System is online'
            send_email_notification(
                config_local.get('Email', 'gmail_server_account',
                                 fallback=None),
                config_local.get('Email', 'gmail_server_password',
                                 fallback=None),
                config_local.get('Email', 'email_to', fallback=None),
                email_subject,
                email_body
            )

        run_strategy()

# GRACEFUL EXIT ON PROGRAM CRASH WITH EMAIL NOTIFICATION OF FAILURE REASON
    except Exception:
        logger.exception('Failed to run strategy')

    if config_local.get('Email', 'email_to', fallback=None):
        args = parse_args()
        log_stream = StringIO()
        email_subject = f'Python Bot STOPPED! --- {args.pair} --- {args.bot}'
        email_body = log_stream.getvalue()
        send_email_notification(
            config_local.get('Email', 'gmail_server_account', fallback=None),
            config_local.get('Email', 'gmail_server_password', fallback=None),
            config_local.get('Email', 'email_to', fallback=None),
            email_subject,
            email_body
        )
    logger.info('Strategy Run over, exit main.py!')
