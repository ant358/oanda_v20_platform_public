[![Build Status](https://travis-ci.com/ant358/oanda_v20_platform_public.svg?branch=master)](https://travis-ci.com/ant358/oanda_v20_platform_public)
[![codecov](https://codecov.io/gh/ant358/oanda_v20_platform_public/branch/master/graph/badge.svg)](https://codecov.io/gh/ant358/oanda_v20_platform_public)
# Automated Trading Platform that runs on Oanda  

This repository is being developed to create a base trading platform to build automated trading strategies on. It is designed to use the Oanda brokerage v20 API. And  it's primary purpose is to collect market prices, evaluate them and execute trades whilst monitoring your trading account. It is designed to run on a virtual machine, however it can easily be run from a local terminal too!

For visualising the trades and charting there are free desktop and web based software programs available from [Oanda](https://www1.oanda.com/) 


If you would like more information about the Oanda API architecture used within this repo or have more questions on obtaining your Oanda tokens and credentials, you can view the full Oanda v20 developer documentation [here](https://developer.oanda.com/rest-live-v20/introduction/)


## Current Features

### Included test strategies:

This repo is designed as a base platform to build strategies upon. As such, everything functional, but it does not contain any profitable automated algorithms. The strategies included can be used to test everything is working. You can view the included algorithms in the strategies/forex_bots_python folder [here.](https://github.com/ant358/oanda_v20_platform_public/tree/master/oanda_v20_platform/strategies/forex_bots_python) 

Included is a simple price printer, a basic order execution bot and a simple RSI execution bot.

### Email and text notifications
As part of the functionality, this platform includes automated email notifications sent for each up and down occurrence of the platform.  If you wish to enable this, you will need pass those arguments into your ```config.ini``` (see below).  This also means you will need to configure a gmail account to use an application password to use for the email sending options if you keep those enabled. There are optional Twilio SMS notifications you can configure as well.
### Database
The ```data/marketdata.py``` module collects and stores the last 60 days of market data. It includes details such as margin rates, average spreads, historic high and lows for all the available trading instruments. It is intended to provide easy access to the data for developing and running trading strategies and for working out the cost of trades and money management strategies.  The marketdata.py module runs to build the database the first time the platform is run. It will only run once for a given day.
  
DB Browser https://sqlitebrowser.org/ is good software for viewing and querying of the database.

## Upstream remote
This repository was originally forked and developed from [Eric Lingren's](https://github.com/Eric-Lingren) version [Oanda V20 Platform Public](https://github.com/Eric-Lingren/Oanda_v20_platform_public). He has other useful server scripts and backtesting systems that are worth checking out and using in conjunction with this code. 

## Installation  
Written and tested on Python 3.7.4, Not yet tested on other Python versions
Tested on Windows, Mac and Linux
The list of required dependencies is in requirements.txt

To instal run:  
```
git clone --branch=master https://github.com/ant358/oanda_v20_platform_public.git ant358/oanda_v20_platform_public  

cd ant358/oanda_v20_platform_public
```
Create a virtual environment and activate it.  
for ref: https://docs.python.org/3/tutorial/venv.html  

Create a ```.env``` file in the ```oanda_v20_platform_public/``` folder and add your account number and token. You can add multiple accounts here e.g. live, practice, different accounts for different strategies etc. The classes in the ```oanda.py``` module are setup to default to ```account=PRACTICE_ACCOUNT``` and ```token=PRACTICE_TOKEN```, when writing strategies to use different accounts simply pass these as keyword arguments to replace the default ones.  
Add ```.env``` to your .gitignore to keep your account details local.  

```
PRACTICE_ACCOUNT=XXX-XXX-XXXXXXXX-XXX
PRACTICE_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  
```
```
$ pip install -e .
$ pip install -r requirements.txt
```
## Usage:

To start the trading platform in a terminal: 
```
cd oanda_v20_platform
python main.py --bot "rsi_bot" --pair "EUR_USD"
```
* change python to python3 on linux

### Additional Config settings
The arguments listed above are all required for operation but there are optional ones available also for email and sms notifications.  To view the full list of all arguments the python script will accept, you can check the ```config.ini``` file contained within the config folder [here]([./config/config.ini](https://github.com/ant358/oanda_v20_platform_public/tree/master/oanda_v20_platform/config))   

### Syntax for args
Currency pairs passed in must adhere to Oandas v20 schema - capital letters separated by an underscore. i.e. You must use ```EUR_USD``` rather than ```eur_usd``` or ```eurusd``` or ```EURUSD``` or some other variation. If you would like more information on this, you can view the Oanda Instrument developer docs [here.](https://developer.oanda.com/rest-live-v20/instrument-ep/)     

  


**None of the automated trading strategies are profitable! They are for demonstration and testing purposes only**
## Disclaimer:

_Trading foreign exchange carries a high level of risk, and may not be suitable for all investors. Past performance is not indicative of future results. Leverage can work against you as well as for you. Before deciding to invest in foreign exchange you should carefully consider your investment objectives, level of experience, and risk appetite. The possibility exists that you could sustain a loss of some or all of your initial investment and therefore you should not invest money that you cannot afford to lose. You should be aware of all the risks associated with foreign exchange trading, and seek advice from an independent financial advisor if you have any doubts._   
\
_I take no responsibility for any losses or gains you may incur from using my software. I also take no responsibility for any architecture, security, or server configurations._   
\
_This software is provided as is. No warranties or guarantees will be provided for its accuracy, completeness, reliability, or security if used within your own environment._
