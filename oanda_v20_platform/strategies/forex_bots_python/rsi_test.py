from oanda.oanda import DataFeed
from indicators.indicators import Indicator
import logging
import time
# import schedule
from threading import Timer


class rsi_test(DataFeed):
    """This system DOES execute trades. This combines the price_printer and
     simple_order_test strategies. This algorithm demonstrates how to use the
     backtrader platform in conjunction with the Oanda API to build a
    custom trading robot that executes trades successfully based upon RSI
     indicator data combined with with three bars of trending prices.

    ****************    WARNING!!!    *********************
    DO NOT RUN THIS ON A LIVE ACCOUNT!  USE A DEMO ACCOUNT!
    YOU WILL LOSE MONEY RUNNING THIS SYSTEM!
    THIS IS FOR FUNCTIONALITY PROOF OF CONCEPT ONLY.
    I WILL NOT BE HELD RESPONSIBLE IF YOU LOOSE MONEY.

    Args:
        see main.py for input args
    """

    def __init__(self, **kwargs):
        """
        Runs the strategy at a specified interval with given arguments.
        """
        super(rsi_test, self).__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        self.profit_target = 5
        self.loss_target = -5
        self.set_indicators()

        self.interval = 30  # seconds
        self.running = False
        self._timer = None
        try:
            self.start()
            self.logger.info('\n-------- RSI Test Strategy '
                             'Initialized use CTRL+C to stop-----------')
            while True:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    self.logger.warning("Strategy Shutting down !")
                    self.stop()
                    break
        except Exception:
            self.logger.exception("Strategy failed to start")

    def __call__(self):
        """
        Handler function for calling the job function at each interval
        and continuing.
        """
        self.running = False  # mark not running
        self.start()          # reset the timer for the next go
        self.job()            # call the job function

    def start(self):
        """
        Starts the interval and lets it run.
        """
        if self.running:
            # Don't start if already running!
            return

        # Create the timer object, start and set state.
        self._timer = Timer(self.interval, self)
        self._timer.start()
        self.running = True

    def stop(self):
        """
        Cancel the interval (no more job function calls).
        """
        if self._timer:
            self._timer.cancel()
        self.running = False
        self._timer = None

    def set_indicators(self):
        self.rsi = Indicator().rsi(ohlc='close', period=14,
                                   pair=self.pair, timeframe='minute', )

    def __next__(self):
        self.set_indicators()
        self.logger.info('\n--------------- NEXT RUN ---------------')
        self.logger.info(f" BID Close Price: {self.data0[0]['bid']['c']}")
        self.logger.info(f" NEW RSI: {self.rsi[0]}")

        bid0 = self.data0[0]['bid']['c']
        bid1 = self.data0[1]['bid']['c']
        bid2 = self.data0[2]['bid']['c']

        matching_trades = self.find_matching_trades()
        # print(matching_trades)
        # No Existing Position. Evaluate Entry Criteria
        if len(matching_trades) == 0:
            if self.rsi[0] <= 30:
                # print("RSI is less than 30")
                if (bid2 > bid1) and (bid1 > bid0):
                    # print('prices are trending down')
                    self.buy_market(5000, self.pair)
            if self.rsi[0] >= 70:
                # print("RSI is greater than than 70")
                if (bid2 < bid1) and (bid1 < bid0):
                    # print('prices are trending up')
                    self.sell_market(5000, self.pair)
        else:  # Position Exists.  Evaluate Exit Criteria.
            position_value = float(matching_trades[0]['unrealizedPL'])
            self.logger.info(f'Checking profit : {position_value}')
            if position_value >= self.profit_target or\
                    position_value <= self.loss_target:
                order_id = matching_trades[0]['id']
                self.close_trade(order_id)

    # PREPARES AND BUNDLES THE TRADING ACTION JOBS FOR EXECUTION
    #  (GET DATA / RUN STRATEGY):
    def job(self):
        # For localhost hardware performance testing
        # DigitalOcean does this natively
        # check_cpu_usage()
        # check_memory_usage()
        first_data_object = self.data0[0]
        self.refresh_data()
        updated_first_data_object = self.data0[0]
        if first_data_object != updated_first_data_object:
            self.__next__()


if __name__ == "__main__":
    rsi_test()
