import argparse
from datetime import datetime, timezone
import pandas as pd
import math
from scipy.stats import gaussian_kde

import matplotlib
matplotlib.use("Agg") # Make matplotlib not trigger rocketship icon
import matplotlib.pyplot as plt

RESULTS_FILE = "results.csv"
IMAGE_FILE = "hotel-bandwidth.png"
STEP = 1 # Mbps
COLORS = {'down': "brown", 'up': "cornflowerblue"}

def plot_dist(start=None, show=True):
    if start is not None and start.tzinfo is None:
        start = start.replace(tzinfo = timezone.utc)
    df = pd.read_csv(RESULTS_FILE,
        index_col='time_utc',
        parse_dates=['time_utc','time_local'])
    df = df.loc[start:]
    df['download_mbps'] = df['download_bps'] / (10**6)
    df['upload_mbps'] = df['upload_bps'] / (10**6)

    max = math.ceil(df[['download_mbps','upload_mbps']].max().max())
    bins_list = range(0, (max + STEP), STEP)

    kde_up = gaussian_kde(df['upload_mbps'])
    kde_down = gaussian_kde(df['download_mbps'])

    fig, ax1 = plt.subplots(figsize=(8,5))
    ax2 = ax1.twinx()

    ax1.hist(df['upload_mbps'],
        label="Up",
        bins=bins_list,
        color=COLORS['up'],
        alpha=0.3
    )
    ax1.hist(df['download_mbps'],
        label="Down",
        bins=bins_list,
        color=COLORS['down'],
        alpha=0.3
    )
    ax2.plot(bins_list, kde_up(bins_list),
        label="Up",
        color=COLORS['up'],
        alpha=0.8
    )
    ax2.plot(bins_list, kde_down(bins_list),
        label="Down",
        color=COLORS['down'],
        alpha=0.8
    )
    # ax1.legend(loc='upper left')
    # ax2.legend(loc='upper right')
    ax2.legend()

    ax1.set_title("Hotel Bandwidth")
    ax1.set_xlabel("Mbps")
    ax1.set_ylabel("Frequency")
    ax2.set_ylabel("Probability Density")

    plt.tight_layout()
    plt.savefig(IMAGE_FILE)
    print(f"Saved histogram to `{IMAGE_FILE}`.")
    if show:
        plt.show()
    plt.close('all')

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Plot hotel bandwidth results")
    parser.add_argument('--start',
        help="the earliest morning to show (inclusive) in YYYY-MM-DD format",
        type=datetime.fromisoformat,
    )
    args = parser.parse_args()
    plot_dist(args.start)