import numpy as np
import pandas as pd


class Dema:

    def __init__(self, historical_data, time_period=200, column="close"):

        self.historical_data = historical_data
        self.time_period = time_period
        self.column = column

    def prev(self):

        ema = self.historical_data[self.column].ewm(
            span=self.time_period, adjust=False).mean()

        dema = 2 * ema - \
            ema.ewm(span=self.time_period, adjust=False).mean()

        return dema

    def next(self, realtime_data):

        split_data = self.historical_data.tail(self.time_period - 1)
        split_data = pd.concat([split_data, realtime_data])

        ema = split_data[self.column].ewm(
            span=self.time_period, adjust=False).mean()

        dema = 2 * ema - \
            ema.ewm(span=self.time_period, adjust=False).mean()

        return dema
