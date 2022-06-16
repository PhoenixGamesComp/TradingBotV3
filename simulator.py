import pandas as pd
from binance_api import get_historical_ohlc_data
from logger import Logger


class Simulator:

    def __init__(self, config):

        self.config = config
        self.logger = Logger()
        self.prepare_simulator_dataset(config)

    def prepare_simulator_dataset(self, config, debug=True):

        if debug:

            self.logger.info(
                "Fetching historical data for {}...".format(config["symbol"]), end=" ")

        self.historical_data = get_historical_ohlc_data(config["symbol"],
                                                        config["past_days"] +
                                                        config["simulation_days"],
                                                        config["time_interval"]
                                                        )
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
                                                       pd.offsets.BDay(config["simulation_days"]-1)].index, inplace=True)

        self.historical_data["high"] = pd.to_numeric(
            self.historical_data["high"])
        self.historical_data["low"] = pd.to_numeric(
            self.historical_data["low"])
        self.historical_data["close"] = pd.to_numeric(
            self.historical_data["close"])
        self.historical_data["open"] = pd.to_numeric(
            self.historical_data["open"])
        self.historical_data["date"] = self.historical_data.index

        if debug:

            self.logger.print("OK")
            self.logger.info(
                "Fetching simulation data for {}...".format(config["symbol"]), end=" ")

        self.simulation_data = get_historical_ohlc_data(config["symbol"],
                                                        config["simulation_days"],
                                                        str(config["refresh_rate"]) + "m"
                                                        )
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
        if debug:

            self.logger.print("OK")

    def get_historical_data(self):

        return self.historical_data

    def get_simulation_data(self):

        return self.simulation_data
