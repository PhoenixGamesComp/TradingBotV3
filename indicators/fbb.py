import pandas as pd


class FBB:

    def __init__(self, historical_data, time_period=200, multiplier=3):

        self.historical_data = historical_data
        self.time_period = time_period
        self.multiplier = multiplier

    def prev(self):

        tp = (self.historical_data["high"] +
              self.historical_data["low"] + self.historical_data["close"]) / 3

        ma = tp.rolling(self.time_period).mean()
        sd = self.multiplier * \
            tp.rolling(self.time_period).std()
        fbb_up = ma + (1 * sd)
        fbb_down = ma - (1 * sd)

        return fbb_up, fbb_down

    def next(self, realtime_data):

        split_data = self.historical_data.tail(self.time_period - 1)
        split_data = pd.concat([split_data, realtime_data])
        tp = (split_data["high"] +
              split_data["low"] + split_data["close"]) / 3

        ma = tp.rolling(self.time_period).mean()
        sd = self.multiplier * \
            tp.rolling(self.time_period).std()
        fbb_up = ma + (1 * sd)
        fbb_down = ma - (1 * sd)

        return fbb_up, fbb_down
