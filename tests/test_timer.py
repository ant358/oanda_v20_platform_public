# from oanda_v20_platform.utils import timer
# import time


# def test_repeat_function_call(capsys):
#     x = timer.RepeatFunctionCall(interval=1)
#     x.start()
#     time.sleep(1)
#     captured = capsys.readouterr()
#     x.stop()
#     message = "RepeatFunctionCall failed to start"
#     assert 'call' in captured, message
