import colorama
import pandas as pd
import speedtest # install speedtest-cli
from datetime import datetime, timezone
from time import sleep
from plot_dist import plot_dist

RESULTS_FILE = "results.csv"
SLEEP_DELAY_S = 3600 # 1 hour
RETRY_DELAY_S = 300 # 5 min
TIME_FORMAT = "%a %Y-%b-%d %H:%M:%S (%z)"

def record_speedtest():
    
    try:
        existing = pd.read_csv(RESULTS_FILE)
    except FileNotFoundError:
        existing = pd.DataFrame()

    local = datetime.now(timezone.utc).astimezone()
    print(
        colorama.Style.BRIGHT +
        f"\nStarting speedtest at {local.strftime(TIME_FORMAT)}..." +
        colorama.Style.RESET_ALL
    )
    results = get_speed()
    results_df = pd.DataFrame({
        'time_utc': [pd.to_datetime(results['timestamp']).round('1s')],
        'time_local': [pd.to_datetime(local).round('1s')],
        'download_bps': [int(results['download'])],
        'upload_bps': [int(results['upload'])],
        'ping_ms': [int(results['ping'])],
        'isp': [results['client']['isp']],
    })

    output = pd.concat([existing, results_df], axis=0)
    print(
        colorama.Fore.GREEN + 
        f"Down {round(results_df.iloc[0]['download_bps']/10**6,2)} Mbps / " +
        f"Up {round(results_df.iloc[0]['upload_bps']/10**6,2)} Mbps / " +
        f"Ping {results_df.iloc[0]['ping_ms']} ms" +
        colorama.Style.RESET_ALL
    )
    output.to_csv(RESULTS_FILE, index=False)
    print(f"Saved results to `{RESULTS_FILE}`.")
    plot_dist(show=False)

def get_speed():
    st = speedtest.Speedtest()
    print("Getting servers...")
    st.get_servers()
    print("Getting best server...")
    st.get_best_server()
    print("Testing download speed...")
    st.download()
    print("Testing upload speed...")
    st.upload()
    return st.results.dict()


if __name__ == "__main__":
    while True:
        try:
            record_speedtest()
            print(f"Waiting {int(SLEEP_DELAY_S/60)} minutes...")
            sleep(SLEEP_DELAY_S)
        except Exception as e:
            print(colorama.Fore.RED + "Could not reach speedtest servers.")
            print(e, colorama.Style.RESET_ALL)
            print(f"Trying again in {int(RETRY_DELAY_S/60)} minutes.")
            sleep(RETRY_DELAY_S)
