from oanda_v20_platform.oanda.oanda import DataFeed
from oanda_v20_platform.indicators.indicators import Indicator
import logging
import time
from threading import Timer


class price_printer(DataFeed):
    """This system does not execute trades. It is a very simple barebones
     algorithm that plugs into the Oanda API and uses that data to print the
     current prices of the selected asset and adds some additional indicators
    Use this for the most rudimentary baseline of how the bots function within
    the backtrader ecosystem.
    Args:
        see main.py for all the input args
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        # self.data0 = self.set_init_data0()
        self.set_indicators()

        self.interval = 30  # seconds
        self.running = False
        self._timer = None
        try:
            self.start()
            self.logger.info("\n--------  Price Printer Strategy "
                             "Initialized use CTRL+C to stop-----------")
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
        self.sma2 = Indicator().sma(self.data0, period=7, ba='bid', ohlc='c')
        self.rsi = Indicator().rsi(ohlc='close', period=14, pair=self.pair,
                                   timeframe='minute')

    def __next__(self):
        self.set_indicators()
        print('\n--------------------------- NEXT RUN ---------------\n')
        self.logger.info(f" BID CLOSE: {self.data0[0]['bid']['c']}")
        self.logger.info(f" ASK CLOSE: {self.data0[0]['ask']['c']}")
        self.logger.info(f" SMA1: {self.sma1}")
        self.logger.info(f" RSI: {self.rsi}")
        print('\n--------------------------- END OF NEXT --------------- \n')

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
    price_printer()
