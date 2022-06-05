import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Trading Bot V3",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "mode", help="Select a mode between 'test' and 'live'.")

    parser.add_argument("-s", "--symbol", type=str,
                        help="define the symbol.", default="BTCUSDT")

    parser.add_argument("-p", "--past-days", type=int,
                        help="define the past days.", default=365)

    parser.add_argument("-t", "--time-interval", type=str,
                        help="define the time interval.", default="1h")

    parser.add_argument("-r", "--refresh-rate", type=int,
                        help="define the refresh rate in ms.", default=3600)

    args = parser.parse_args()
    config = vars(args)
    print(config)
