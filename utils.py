import time

class PostObject:
    """ A custom class to organise different posting types """

    def __init__(self, post_Type, interval=None):
        """ Sets up and returns a PostObject object

                -- ARGUMENTS --

            :post_Type: is the the number of requests that can be made to an
            endpoint during a period

            :period: is the duration of time in seconds in which the requests
            can be made
        """

        self.auto = False
        self.intervals = False

        if post_Type == "auto":
            self.auto = True
        elif post_Type == "intervals":
            self.intervals = True
            if not interval:
                interval = 1800
            self.interval = interval

class Post:
    """ A non callable class intended to simplify the PostObject class """

    def auto():
        """ A method to create an 'auto' PostObject instance """
        return PostObject("auto")

    def manual():
        """  A method to create a 'manual' PostObject instance """
        return PostObject("manual")

    def intervals(seconds: int = 0, minutes: int = 0, hours: int = 0):
        """  A method to create an 'intervals' PostObject instance. The
            arguments provided are cumulative and so are added together

                -- ARGUMENTS --

            :seconds: is part of the duration of the interval (in seconds)

            :minutes: is part of the duration of the interval (in minutes)

            :hours: is part of the duration of the interval (in hours)
            """
        interval = seconds + minutes*60 + hours*3600
        return PostObject("intervals", interval=interval)

class Ratelimit:
    """ A custom class to emulate api ratelimits """

    period_start = 0
    requests_made = 0

    def __init__(self, requests: float, period: float):
        """ Sets up the ratelimits and returns a Ratelimit object

                -- ARGUMENTS --

            :requests: is the number of requests that can be made to an
            endpoint during a period

            :period: is the duration of time in seconds in which the number of
            requests can be made
        """
        self.requests = requests
        self.period = period

    def emulate(self):
        """ Emulates a request """

        timestamp = time.time()
        if timestamp >= self.period_start + self.period:
            self.period_start = timestamp
            self.requests_made = 1
        elif self.requests_made < self.requests:
            self.requests_made += 1

    def is_ratelimited(self, emulate=False):
        """ Checks if the ratelimit has been reached

                -- ARGUMENTS --

            :emulate: will additionally call the emulate function
        """

        if emulate:
            self.emulate()

        timestamp = time.time()
        if timestamp >= self.period_start + self.period:
            return False
        elif self.requests_made < self.requests:
            return False
        return True

    def until_reset(self):
        """ Returns the amount of time until the endpoint is no longer
            ratelimited
        """

        timestamp = time.time()

        seconds = (self.period_start + self.period) - timestamp
        if timestamp >= self.period_start + self.period:
            seconds = 0

        return seconds