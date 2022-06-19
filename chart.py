import mplfinance as mpf
import datetime
import sys


def create_plot(data, ap=[], ax=None):

    ohlc = data.filter(
        ["open", "high", "low", "close"], axis=1).copy()
    ohlc = ohlc.astype(float)

    mc = mpf.make_marketcolors(down="#EDA247", up="#57C4AD", edge={
        "down": "#DB4325", "up": "#006164"}, wick={"down": "#DB4325", "up": "#006164"}, alpha=0.8)

    s = mpf.make_mpf_style(base_mpf_style="nightclouds",
                           marketcolors=mc, gridstyle="")
    if ax is None:

        fig, axes = mpf.plot(ohlc, type="candle", style=s,
                             returnfig=True, show_nontrading=True, addplot=ap, warn_too_much_data=sys.maxsize, block=False)

        return fig, axes

    else:

        mpf.plot(ohlc, type="candle", style=s, ax=ax,
                 returnfig=True, show_nontrading=True, addplot=ap, warn_too_much_data=sys.maxsize, block=False)

        return None
