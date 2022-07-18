import pandas as pd
from binance_api import get_historical_ohlc_data
from logger import Logger
import sys
import mplfinance as mpf
import matplotlib.animation as animation
from chart import create_plot
from indicators.dema import Dema
from indicators.fbb import FBB
from indicators.supertrend import Supertrend


class Simulator:

    def __init__(self, config):

        self.config = config
        self.logger = Logger()
        self.prepare_simulator_dataset(config)

        self.dema = Dema(self.historical_data)
        self.fbb = FBB(self.historical_data)
        self.supertrend = Supertrend(self.historical_data)

        self.curr = 0
        self.resample_period = config["time_interval"]
        self.resample_map = {'open': 'first',
                             'high': 'max',
                             'low': 'min',
                             'close': 'last'}

        self.visible_data = 50

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

        self.plot_data = self.plot_data.tail(self.visible_data)
        self.axes[0].clear()

        # DEMA
        dema_data = self.dema.next(self.plot_data.tail(1))
        dema_plot = mpf.make_addplot(dema_data.tail(self.visible_data), width=0.75,
                                     color="c", ax=self.axes[0])

        # FBB
        fbb_data = self.fbb.next(self.plot_data.tail(1))
        fbb_up_plot = mpf.make_addplot(
            fbb_data[0].tail(self.visible_data), width=0.75, color="r", ax=self.axes[0])
        fbb_down_plot = mpf.make_addplot(
            fbb_data[1].tail(self.visible_data), width=0.75, color="r", ax=self.axes[0])

        # Supertrend
        supertrend_data = self.supertrend.next(self.plot_data.tail(1))
        supertrend_lower_plot = mpf.make_addplot(
            supertrend_data[1].tail(self.visible_data), width=0.75, color="r", ax=self.axes[0])
        supertrend_upper_plot = mpf.make_addplot(
            supertrend_data[2].tail(self.visible_data), width=0.75, color="g", ax=self.axes[0])

        create_plot(self.plot_data,
                    ap=[
                        dema_plot,
                        fbb_up_plot,
                        fbb_down_plot,
                        supertrend_lower_plot,
                        supertrend_upper_plot],
                    ax=self.axes[0])

    def run(self):

        self.historical_data = self.historical_data.resample(
            self.resample_period).agg(self.resample_map).dropna()

        self.plot_data = self.historical_data.tail(self.visible_data)

        # DEMA
        dema_data = self.dema.prev()
        dema_plot = mpf.make_addplot(
            dema_data.tail(self.visible_data), width=0.75, color="c")

        # FBB
        fbb_data = self.fbb.prev()
        fbb_up_plot = mpf.make_addplot(
            fbb_data[0].tail(self.visible_data), width=0.75, color="r")
        fbb_down_plot = mpf.make_addplot(
            fbb_data[1].tail(self.visible_data), width=0.75, color="r")

        # Supertrend
        supertrend_data = self.supertrend.prev()

        print(supertrend_data[1])
        print(supertrend_data[2])
        input("...")

        supertrend_lower_plot = mpf.make_addplot(
            supertrend_data[1].tail(self.visible_data), width=0.75, color="r")
        supertrend_upper_plot = mpf.make_addplot(
            supertrend_data[2].tail(self.visible_data), width=0.75, color="g")

        self.fig, self.axes = create_plot(
            self.plot_data, ap=[
                dema_plot,
                fbb_up_plot,
                fbb_down_plot,
                supertrend_lower_plot,
                supertrend_upper_plot])
        self.ani = animation.FuncAnimation(
            self.fig, self.animate, interval=25)
        mpf.show()

    def get_historical_data(self):

        return self.historical_data

    def get_simulation_data(self):

        return self.simulation_data
