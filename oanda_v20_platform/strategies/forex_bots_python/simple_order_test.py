from oanda.oanda import DataFeed
from indicators.indicators import Indicator
import logging
import time
from threading import Timer


class simple_order_test(DataFeed):
    """This system DOES execute trades. This is very similar to Backtraders
     example code documentation. This is used to demonstrate a proof of concept
     of order execution within this platform. It simply looks for 2 consecutive
     rising or falling bars and executes a position if there are
     no open positions

    ****************    WARNING!!!    ********************************
    DO NOT RUN THIS ON A LIVE ACCOUNT!  USE A DEMO ACCOUNT!
    YOU WILL LOSE MONEY RUNNING THIS SYSTEM!
    THIS IS FOR FUNCTIONALITY PROOF OF CONCEPT ONLY.
    I WILL NOT BE HELD RESPONSIBLE IF YOU LOOSE MONEY.

    Args:
        DataFeed ([type]): [description]
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        # self.data0 = self.set_init_data0()
        self.profit_target = 1
        self.loss_target = -1
        self.set_indicators()

        self.interval = 30  # seconds
        self.running = False
        self._timer = None
        try:
            self.start()
            self.logger.info('\n-------- Simple Test Strategy'
                             ' Initialized use CTRL+C to stop-----------')
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
        self.sma1 = Indicator().sma(self.data0, period=14, ba='bid', ohlc='c')

    def __next__(self):
        self.set_indicators()
        self.logger.info('\n--------------- NEXT RUN ---------------\n')
        self.logger.info(f" BID Close Price: {self.data0[0]['bid']['c']}")

        bid0 = self.data0[0]['bid']['c']
        bid1 = self.data0[1]['bid']['c']

        matching_trades = self.find_matching_trades()
        # No Existing Position. Evaluate Entry Criteria
        if len(matching_trades) == 0:
            if bid0 > bid1:  # Prices are Rising
                self.buy_market(5000, self.pair)
            if bid0 < bid1:  # Prices Are Falling
                self.sell_market(5000, self.pair)
        else:  # There is an existing position.  Evaluate Exit Criteria.
            position_value = float(matching_trades[0]['unrealizedPL'])
            if position_value >= self.profit_target or\
                    position_value <= self.loss_target:
                order_id = matching_trades[0]['id']
                self.close_trade(order_id)

    # PREPARES AND BUNDLES THE TRADING ACTION JOBS FOR EXECUTION
    # (GET DATA / RUN STRATEGY):
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
    simple_order_test()
