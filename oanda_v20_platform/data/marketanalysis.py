# %%
# import json 
# import datetime
import numpy as np
import pandas as pd 
from pandas import json_normalize
import sqlalchemy as sq
# import requests
from oanda.oanda import Account
# import os.path
import logging
from utils.fileops import get_abs_path 


class MarketAnalysis(Account):

    """
    Normalise the market. Get everything priced in dollars so that the assets can be compared. 
    Calculate the usdx (USD Index) to monitor the price of the dollar alone
    Calculate Returns - which are the percent change and can aggregate accross assets
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

        # self.normalise()


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
        df = pd.read_sql_table(instrument, 
                                con=self.engine, 
                                columns=['close', 'N'],
                                index_col='time',
                                parse_dates='time')
        return df


    def get_full_table(self, instrument):
        """Gets the full table for an instrument, 
        sets the index to time and returns a dataframe
        """
        df = pd.read_sql_table(instrument, 
                                con=self.engine, 
                                index_col='time',
                                parse_dates='time')
        return df


    def exp_table(self, table_name, df):
        """Sends a dataframe to the database table replacing previous data"""
        df.to_sql(table_name, if_exists='replace', con=self.engine)

    ######### Normalise Market data to USD ##################################

    def aussie_stocks(self):
        au200aud = self.get_table('AU200_AUD')
        audusd = self.get_table('AUD_USD')
        # create new df by dividing two df's
        au200 = au200aud[['close', 'N']].multiply(audusd['close'], axis=0) 
        # add returns
        au200['ReturnsUSD'] = self.discrete_returns(au200)
        au200['LogReturnsUSD'] = self.log_returns(au200)
        # return au200
        # self.exp_table('AU200_USD', au200)


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
            name_usd = self.get_full_table(i)
            name_usd['ReturnsUSD'] = self.discrete_returns(name_usd)
            name_usd['LogReturnsUSD'] = self.log_returns(name_usd)
            # self.exp_table(i.split('_')[0], name_usd)


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
            # usd_name = i.lower()
            name = i.split('_')[1]
            usd_name = self.get_table(i)
            name_usd = usd_name[['close', 'N']].pow(-1, axis=0)
            name_usd['ReturnsUSD'] = self.discrete_returns(name_usd)
            name_usd['LogReturnsUSD'] = self.log_returns(name_usd)
            # self.exp_table(name + '_USD', name_usd)


    def hk_stocks(self):
        hk33hkd = self.get_table('HK33_HKD')
        usdhkd = self.get_table('USD_HKD')
        hk33 = hk33hkd[['close', 'N']].divide(usdhkd['close'], axis=0)
        hk33['ReturnsUSD'] = self.discrete_returns(hk33)
        hk33['LogReturnsUSD'] = self.log_returns(hk33)
        # self.exp_table('HK33_USD', hk33)


    def singapore_stocks(self):
        sg30sgd = self.get_table('SG30_SGD')
        usdsgd = self.get_table('USD_SGD')
        sg30 = sg30sgd[['close', 'N']].divide(usdsgd['close'], axis=0)
        sg30['ReturnsUSD'] = self.discrete_returns(sg30)
        sg30['LogReturnsUSD'] = self.log_returns(sg30)
        # self.exp_table('SG30_USD', sg30)


    def usdx(self):
            """calculate the U.S. dollar index
            table
            """
            c = 50.14348112
            euro = self.get_table('EUR_USD').pow(-0.576, axis=0)
            yen = self.get_table('USD_JPY').pow(0.136, axis=0)
            pound = self.get_table('GBP_USD').pow(-0.119, axis=0)
            cad = self.get_table('USD_CAD').pow(0.091, axis=0)
            sek = self.get_table('USD_SEK').pow(0.042, axis=0)
            swiss = self.get_table('USD_CHF').pow(0.036, axis=0)
            # TODO must be a better way supplying a list of df to multiply doesn't seem to work
            usdx = euro.multiply(c, axis=0) 
            usdx = usdx.multiply(yen, axis=0)
            usdx = usdx.multiply(pound, axis=0)
            usdx = usdx.multiply(cad, axis=0)
            usdx = usdx.multiply(sek, axis=0)
            usdx = usdx.multiply(swiss, axis=0)
            usdx.drop('N', axis=1, inplace=True)
            usdx['ReturnsUSD'] = self.discrete_returns(usdx)
            usdx['LogReturnsUSD'] = self.log_returns(usdx)
            # self.exp_table('USDX', usdx)
            return usdx


    def cable_stks_and_bonds(self):
        uk100gbp = self.get_table('UK100_GBP')
        uk10ybgbp = self.get_table('UK10YB_GBP')
        gbpusd = self.get_table('GBP_USD')
        uk100 = uk100gbp[['close', 'N']].multiply(gbpusd['close'], axis=0)
        uk10yb = uk10ybgbp[['close', 'N']].multiply(gbpusd['close'], axis=0)
        uk100['ReturnsUSD'] = self.discrete_returns(uk100)
        uk100['LogReturnsUSD'] = self.log_returns(uk100)
        uk10yb['ReturnsUSD'] = self.discrete_returns(uk10yb)
        uk10yb['LogReturnsUSD'] = self.log_returns(uk10yb)
        # self.exp_table('UK100_USD', uk100)
        # self.exp_table('UK10YB_USD', uk10yb)


    def euro_stks_and_bonds(self):
        euro_conv = [ 'DE10YB_EUR', 'DE30_EUR', 'EU50_EUR', 'FR40_EUR', 'NL25_EUR']
        eurusd = self.get_table('EUR_USD')
        for i in euro_conv:
            name = i.split('_')[0]
            name_eur = self.get_table(i)
            name_usd = name_eur[['close', 'N']].multiply(eurusd['close'], axis=0)
            name_usd['ReturnsUSD'] = self.discrete_returns(name_usd)
            name_usd['LogReturnsUSD'] = self.log_returns(name_usd)
            # self.exp_table(name + '_USD', name_usd)
            return name_usd


    def normalise(self):
        self.cable_stks_and_bonds()
        self.euro_stks_and_bonds()
        self.usdx()
        self.singapore_stocks()
        self.hk_stocks()
        self.reverse_usd()
        self.straight_usd()
        self.aussie_stocks()

if __name__=="__main__":
    test = MarketAnalysis()
