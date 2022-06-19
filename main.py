import argparse
import pandas as pd
from chart import create_plot
from simp_zoom import zoom_factory
from simulator import Simulator
import mplfinance as mpf


def arg_handler():

    parser = argparse.ArgumentParser(description="Trading Bot V3",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "mode", help="Select a mode between 'test' and 'live'.")

    parser.add_argument("-s", "--symbol", type=str,
                        help="define the symbol.", default="BTCBUSD")

    parser.add_argument("-p", "--past-days", type=int,
                        help="define the past days.", default=365)

    parser.add_argument("-t", "--time-interval", type=str,
                        help="define the time interval.", default="1h")

    parser.add_argument("-r", "--refresh-rate", type=int,
                        help="define the refresh rate in m.", default=1)

    parser.add_argument("-d", "--simulation-days", type=int,
                        help="define the simulation days", default=30)

    args = parser.parse_args()
    config = vars(args)
    return config


def main():

    config = arg_handler()
    simulator = Simulator(config)
    simulator.run()

    mpf.show()


if __name__ == "__main__":

    main()
