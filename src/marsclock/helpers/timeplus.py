from time import *

# Expand python to include micosecond sleep
try:
    sleep_ms(0)
except AttributeError as err:

    def sleep_ms(secs):
        sleep(secs / 1000)