import pandas as pd
from binance_api import get_historical_ohlc_data
from logger import Logger
import sys
import mplfinance as mpf
import matplotlib.animation as animation
from chart import create_plot


class Simulator:

    def __init__(self, config):

        self.config = config
        self.logger = Logger()
        self.prepare_simulator_dataset(config)
        self.curr = 0
        self.resample_period = config["time_interval"]
        self.resample_map = {'open': 'first',
                             'high': 'max',
                             'low': 'min',
                             'close': 'last'}

    def prepare_simulator_dataset(self, config, debug=True):

        # Head older, tail latest

        if debug:

            self.logger.info(
                "Fetching historical data for {}...".format(config["symbol"]), end=" ")

        try:

            self.historical_data = get_historical_ohlc_data(config["symbol"],
                                                            config["past_days"],
                                                            config["time_interval"]
                                                            )
        except Exception as e:

            if debug:

                self.logger.print("ERROR")
                self.logger.error(
                    "Fetching historical data failed with exception: \n{}".format(e))
                self.logger.error("Terminating bot...")
                sys.exit(1)

        if debug:

            self.logger.print("OK")
            self.logger.info(
                "Preparing historical data...", end=" ")

        self.historical_data.rename(
            columns={"open_date_time": "date"}, inplace=True)
        self.historical_data["date"] = pd.to_datetime(
            self.historical_data["date"])
        self.historical_data.set_index("date", inplace=True)

        self.historical_data.drop(self.historical_data[self.historical_data.index >= self.historical_data.index.max().date() -
                                                       pd.offsets.Day(config["simulation_days"]-1)].index, inplace=True)
        self.historical_data["high"] = pd.to_numeric(
            self.historical_data["high"])
        self.historical_data["low"] = pd.to_numeric(
            self.historical_data["low"])
        self.historical_data["close"] = pd.to_numeric(
            self.historical_data["close"])
        self.historical_data["open"] = pd.to_numeric(
            self.historical_data["open"])
        self.historical_data["date"] = self.historical_data.index
        self.historical_data.sort_index(inplace=True)

        if debug:

            self.logger.print("OK")
            self.logger.info(
                "Fetching simulation data for {}...".format(config["symbol"]), end=" ")

        try:

            self.simulation_data = get_historical_ohlc_data(config["symbol"],
                                                            config["simulation_days"],
                                                            str(config["refresh_rate"]) + "m"
                                                            )

        except Exception as e:

            if debug:

                self.logger.print("ERROR")
                self.logger.error(
                    "Fetching simulation data failed with exception: \n{}".format(e))
                self.logger.error("Terminating bot...")
                sys.exit(1)

        if debug:

            self.logger.print("OK")
            self.logger.info(
                "Preparing historical data...", end=" ")

        self.simulation_data["high"] = pd.to_numeric(
            self.simulation_data["high"])
        self.simulation_data["low"] = pd.to_numeric(
            self.simulation_data["low"])
        self.simulation_data["close"] = pd.to_numeric(
            self.simulation_data["close"])
        self.simulation_data["open"] = pd.to_numeric(
            self.simulation_data["open"])

        self.simulation_data.rename(
            columns={"open_date_time": "date"}, inplace=True)
        self.simulation_data["date"] = pd.to_datetime(
            self.simulation_data["date"])
        self.simulation_data.set_index("date", inplace=True)
        self.simulation_data.sort_index(inplace=True)

        self.simulation_data = self.simulation_data[~(self.simulation_data.index <
                                                      self.historical_data.index[-1])]

        if debug:

            self.logger.print("OK")

    def fetch_next(self):

        self.curr = self.curr + 1
        if self.curr >= len(self.simulation_data):

            return None

        nxt = self.simulation_data.iloc[self.curr].to_dict()
        nxt["date"] = self.simulation_data.index[self.curr]
        return nxt

    def animate(self, ival):

        nxt = self.fetch_next()

        if nxt is None:

            self.logger.warn("Simulation reached to its end.")
            self.logger.warn("Terminating simulator... OK")

            self.ani.event_source.interval *= 3
            if self.ani.event_source.interval > 12000:

                exit()

            return

        nxt = {nxt["date"]: nxt}
        nxt = pd.DataFrame.from_dict(nxt, orient="index")

        self.plot_data = pd.concat([self.plot_data, nxt])

        self.plot_data = self.plot_data.resample(
            self.resample_period).agg(self.resample_map).dropna()

        self.plot_data = self.plot_data.tail(25)
        self.axes[0].clear()
        create_plot(self.plot_data, ax=self.axes[0])

    def run(self):

        self.historical_data = self.historical_data.resample(
            self.resample_period).agg(self.resample_map).dropna()

        self.plot_data = self.historical_data.tail(25)

        self.fig, self.axes = create_plot(self.plot_data)
        self.ani = animation.FuncAnimation(
            self.fig, self.animate, interval=25)
        mpf.show()

    def get_historical_data(self):

        return self.historical_data

    def get_simulation_data(self):

        return self.simulation_data
