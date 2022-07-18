import pandas as pd
import numpy as np


class Supertrend:

    def __init__(self, historical_data, atr_period=12, multiplier=3):

        self.historical_data = historical_data
        self.atr_period = atr_period
        self.multiplier = multiplier

    def __calc(self, data, high, low, close):

        # calculate ATR
        price_diffs = [high - low,
                       high - close.shift(),
                       close.shift() - low]
        true_range = pd.concat(price_diffs, axis=1)
        true_range = true_range.abs().max(axis=1)
        # default ATR calculation in supertrend indicator
        atr = true_range.ewm(alpha=1/self.atr_period,
                             min_periods=self.atr_period).mean()
        # df['atr'] = df['tr'].rolling(atr_period).mean()

        # HL2 is simply the average of high and low prices
        hl2 = (high + low) / 2
        # upperband and lowerband calculation
        # notice that final bands are set to be equal to the respective bands
        final_upperband = hl2 + \
            (self.multiplier * atr)
        final_lowerband = hl2 - \
            (self.multiplier * atr)

        # initialize Supertrend column to True
        supertrend = [True] * len(data.index)

        for i in range(1, len(data.index)):
            curr, prev = i, i-1

        # if current close price crosses above upperband
        if close[curr] > final_upperband[prev]:
            supertrend[curr] = True
        # if current close price crosses below lowerband
        elif close[curr] < final_lowerband[prev]:
            supertrend[curr] = False
        # else, the trend continues
        else:
            supertrend[curr] = supertrend[prev]

        # adjustment to the final bands
        if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
            final_lowerband[curr] = final_lowerband[prev]
        if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
            final_upperband[curr] = final_upperband[prev]

        # to remove bands according to the trend direction
        if supertrend[curr] == True:
            final_upperband[curr] = np.nan
        else:
            final_lowerband[curr] = np.nan

        return supertrend[curr], final_lowerband, final_upperband

    def prev(self):

        high = self.historical_data["high"]
        low = self.historical_data["low"]
        close = self.historical_data["close"]

        return self.__calc(self.historical_data, high, low, close)

    def next(self, realtime_data):

        split_data = pd.concat([self.historical_data, realtime_data])

        high = split_data["high"]
        low = split_data["low"]
        close = split_data["close"]

        return self.__calc(split_data, high, low, close)
