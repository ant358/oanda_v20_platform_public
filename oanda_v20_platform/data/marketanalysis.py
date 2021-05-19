# %%
import json 
import datetime
import numpy as np
import pandas as pd 
from pandas import json_normalize
import sqlalchemy as sq
import requests
from oanda.oanda import Account
import os.path
import logging
from utils.fileops import get_abs_path 


class MarketAnalysis(Account):

    """
    Normalise the market. Get everything priced in dollars so that the assets can be compared. 
    Calculate the usdx (USD Index) to monitor the price of the dollar alone
    Calculate Returns - which are percent change and can aggregate accross assets
    Calculate Log Returns - which can aggregate over time
    Generate a table for each asset in dollar terms 




    Args:
        db_path str, default='data/marketdata.db': 
            The path to the database from the directory where this class is being run.
    """
    def __init__(self, db_path=get_abs_path(['oanda_v20_platform','data', 'marketdata.db']), **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        # setup connection to the database
        self.db_path=db_path
        self.engine = sq.create_engine(f'sqlite:///{self.db_path}')

        self.normalise()


    ########### Table calculations ################################

    def discrete_returns(self, df):
        """Calculate the discrete returns. 
        The difference between the daily close price
        """
        dr = df['close'].pct_change()
        return dr

    def log_returns(self, df):
        """Calculate the log returns. 
        The log difference between the daily close price
        """
        lr = np.log(df['close'] /df['close'].shift(1))
        return lr



    def get_table(self, instrument):
        """Gets the close prices and N for an instrument, 
        sets the index to time and returns a dataframe
        """
        return pd.read_sql_table(instrument, 
                                con=self.engine, 
                                columns=['time', 'close', 'N'], 
                                index_col='time', 
                                parse_dates='time')

    def exp_table(self, table_name, df):
        """Sends a dataframe to the database table replacing previous data"""
        df.to_sql(table_name, if_exists='replace', con=self.engine)

    ######### Normalise Market data to USD ##################################

    def aussie_stocks(self):
        au200aud = self.get_table('AU200_AUD')
        audusd = self.get_table('AUD_USD')
        # create new df by dividing two df's
        au200 = round(au200aud[['close']] / audusd[['close']], 2)
        # add returns
        au200['ReturnsUSD'] = self.discrete_returns(au200)
        au200['LogReturnsUSD'] = self.log_returns(au200)
        au200['Dollar_N'] = round(au200aud['N'] / audusd['close'], 2)
        self.exp_table('AU200', au200)


    def straight_usd(self):
        straight_dollar = [ 'AUD_USD', 
                            'BCO_USD', 
                            'CN50_USD', 
                            'CORN_USD', 
                            'EUR_USD', 
                            'GBP_USD', 
                            'IN50_USD', 
                            'JP225_USD', 
                            'NAS100_USD', 
                            'NATGAS_USD', 
                            'NZD_USD', 
                            'SOYBN_USD', 
                            'SPX500_USD', 
                            'SUGAR_USD', 
                            'TWIX_USD', 
                            'US2000_USD', 
                            'US30_USD', 
                            'USB02Y_USD', 
                            'USB05Y_USD', 
                            'USB10Y_USD', 
                            'USB30Y_USD', 
                            'WHEAT_USD', 
                            'WTICO_USD', 
                            'XAG_USD', 
                            'XAU_USD', 
                            'XCU_USD', 
                            'XPD_USD', 
                            'XPT_USD'] 
        for i in straight_dollar:
            name_usd = i.lower()
            name = i.lower().split('_')[0]
            name_usd = self.get_table(i)
            name = name_usd[['close']]
            name['ReturnsUSD'] = self.discrete_returns(name)
            name['LogReturnsUSD'] = self.log_returns(name)
            name['Dollar_N'] = name_usd['N']
            self.exp_table(i.split('_')[0], name)


    def reverse_usd(self):
        reverse_dollar = [  'USD_CAD',
                            'USD_CHF', 
                            'USD_CNH',
                            'USD_CZK', 
                            'USD_DKK', 
                            'USD_HKD', 
                            'USD_HUF', 
                            'USD_INR', 
                            'USD_JPY', 
                            'USD_MXN', 
                            'USD_NOK', 
                            'USD_PLN',  
                            'USD_SEK', 
                            'USD_SGD', 
                            'USD_THB', 
                            'USD_TRY', 
                            'USD_ZAR']
        for i in reverse_dollar:
            usd_name = i.lower()
            name = i.lower().split('_')[1]
            usd_name = self.get_table(i)
            name = usd_name[['close']]**-1
            name['ReturnsUSD'] = self.discrete_returns(name)
            name['LogReturnsUSD'] = self.log_returns(name)
            name['Dollar_N'] = usd_name['N']**-1
            self.exp_table(i.split('_')[1], name)


    def hk_stocks(self):
        hk33hkd = self.get_table('HK33_HKD')
        usdhkd = self.get_table('USD_HKD')
        hk33 = round(hk33hkd[['close']] * usdhkd[['close']], 1)
        hk33['ReturnsUSD'] = self.discrete_returns(hk33)
        hk33['LogReturnsUSD'] = self.log_returns(hk33)
        hk33['Dollar_N'] = hk33hkd['N'] * usdhkd['close']
        self.exp_table('HK33', hk33)


    def singapore_stocks(self):
        sg30sgd = self.get_table('SG30_SGD')
        usdsgd = self.get_table('USD_SGD')
        sg30 = round(sg30sgd[['close']] * usdsgd[['close']], 1)
        sg30['ReturnsUSD'] = self.discrete_returns(sg30)
        sg30['LogReturnsUSD'] = self.log_returns(sg30)
        sg30['Dollar_N'] = sg30sgd['N'] * usdsgd['close']
        self.exp_table('SG30', sg30)


    def usdx(self):
            """calculate the U.S. dollar index
            table
            """
            c = 50.14348112
            euro = self.get_table('EUR_USD')[['close']]**-0.576
            yen = self.get_table('USD_JPY')[['close']]**0.136
            pound = self.get_table('GBP_USD')[['close']]**-0.119
            cad = self.get_table('USD_CAD')[['close']]**0.091
            sek = self.get_table('USD_SEK')[['close']]**0.042
            swiss = self.get_table('USD_CHF')[['close']]**0.036
            usdx = c * euro * yen * pound * cad * sek * swiss
            usdx['ReturnsUSD'] = self.discrete_returns(usdx)
            usdx['LogReturnsUSD'] = self.log_returns(usdx)
            self.exp_table('USDX', usdx)


    def cable_stks_and_bonds(self):
        uk100gbp = self.get_table('UK100_GBP')
        uk10ybgbp = self.get_table('UK10YB_GBP')
        gbpusd = self.get_table('GBP_USD')
        uk100 = uk100gbp[['close']] / gbpusd[['close']]
        uk10yb = uk10ybgbp[['close']] / gbpusd[['close']]
        uk100['ReturnsUSD'] = self.discrete_returns(uk100)
        uk100['LogReturnsUSD'] = self.log_returns(uk100)
        uk100['Dollar_N'] = uk100gbp['N'] / gbpusd['close']
        uk10yb['ReturnsUSD'] = self.discrete_returns(uk10yb)
        uk10yb['LogReturnsUSD'] = self.log_returns(uk10yb)
        uk10yb['Dollar_N'] = uk10ybgbp['N'] / gbpusd['close']
        self.exp_table('UK100', uk100)
        self.exp_table('UK10YB', uk10yb)


    def euro_stks_and_bonds(self):
        euro_conv = [ 'DE10YB_EUR', 'DE30_EUR', 'EU50_EUR', 'FR40_EUR', 'NL25_EUR']
        eurusd = self.get_table('EUR_USD')
        for i in euro_conv:
            name_eur = i.lower()
            name = i.lower().split('_')[0]
            name_eur = self.get_table(i)
            name = name_eur[['close']] / eurusd[['close']]
            name['ReturnsUSD'] = self.discrete_returns(name)
            name['LogReturnsUSD'] = self.log_returns(name)
            name['Dollar_N'] = name_eur['N'] / eurusd['close']
            self.exp_table(i.split('_')[0], name)


    def normalise(self):
        self.cable_stks_and_bonds()
        self.euro_stks_and_bonds()
        self.usdx()
        self.singapore_stocks()
        self.hk_stocks()
        self.reverse_usd()
        self.straight_usd()
        self.aussie_stocks()
# %%
test = MarketAnalysis()

# %%
