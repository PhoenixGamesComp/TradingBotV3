import mplfinance as mpf
import datetime
import sys


def create_plot(data, ap=[]):

    ohlc = data.filter(
        ["open", "high", "low", "close"], axis=1).copy()
    ohlc = ohlc.astype(float)

    mc = mpf.make_marketcolors(down="#EDA247", up="#57C4AD", edge={
        "down": "#DB4325", "up": "#006164"}, wick={"down": "#DB4325", "up": "#006164"}, alpha=0.8)

    s = mpf.make_mpf_style(base_mpf_style="nightclouds",
                           marketcolors=mc, gridstyle="")
    fig, ax = mpf.plot(ohlc, type="candle", style=s,
                       returnfig=True, show_nontrading=True, addplot=ap, warn_too_much_data=sys.maxsize, block=False)

    xmin = data[len(data)-10:].index[0]
    xmax = data[len(data)-10:].index[-1]
    ax[0].set_xlim(xmin, xmax + datetime.timedelta(days=1))

    ymin = min(data.loc[xmin]["low"], data.loc[xmax]["low"])
    ymax = max(data.loc[xmin]["high"], data.loc[xmax]["high"])
    ax[0].set_ylim(ymin, ymax)

    return fig, ax
