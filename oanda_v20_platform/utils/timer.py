from threading import Timer
from datetime import datetime
import time


def amIworking(i=[0]):
    print(f"call: {i[0]}, function called at:", datetime.now())
    i[0] += 1


class RepeatFunctionCall(Timer):
    """Repeats the call to a function every x seconds.
    Note waits the interval before the first call.

    Args:
        interval (float): The number of seconds between calls to the function.
            default = 30 seconds
        function (name): The function name to call.
            default = amIworking a simple test function

    """

    def __init__(self, interval=30, function=amIworking,
                 **kwargs):
        super().__init__(interval, function, kwargs=kwargs)

        self.interval = interval  # seconds
        self.running = False
        self._timer = None
        self.function = function
        try:
            self.start()
            while True:
                try:
                    time.sleep(1)
                except KeyboardInterrupt as e:
                    self.stop()
                    print(e)
                    break
        except Exception as e:
            print(e)

    def __call__(self):
        """
        Handler function for calling the job function at each interval
        and continuing.
        """
        self.running = False  # mark not running
        self.start()          # reset the timer for the next go
        self.function()       # call the function to repeat

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


if __name__ == "__main__":
    checktimer = RepeatFunctionCall()
    checktimer.start()

