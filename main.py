import pandas as pd
import asyncio
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from archiver import Archiver
from utils import DataUtils

HLS_PVS = ['TU-11C:SS-HLS-Ax48NW5:Level-Mon', 'TU-01C:SS-HLS-Ax16SE4:Level-Mon']
TIDES_PV = ['LNLS:MARE:EAST']
RF_PV = ['RF-Gen:GeneralFreq-RB']
WELL_PV = ['INF:POC01:Pressure_mca']

def get_data_from_archiver(pvs, timespam) -> pd.DataFrame:
    data = asyncio.run(Archiver.request_data(pvs, timespam, 5))
    return data

def get_local_data(filepath) -> pd.DataFrame:
    data = pd.read_excel(filepath)
    data.index = pd.DatetimeIndex(data['datetime'])
    data.drop(columns=['datetime'], inplace=True)
    return data

def plot_timeseries(xy_pais: dict):
    _, ax = plt.subplots(figsize=(15,7))

    ax_rf = ax.twinx()
    
    ax.plot(xy_pais['hls'][0], xy_pais['hls'][1], color='darkorange', label='HLS')
    ax_rf.plot(xy_pais['rf'][0], xy_pais['rf'][1], color='green', label='Storage Ring RF')

    ax.set_ylabel(u"Height [mm]")
    ax_rf.set_ylabel('Freq. [Hz]')
    
    ax.legend()
    
    ax.yaxis.labelpad = 10
    locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.tick_params(axis='both')

    ax.grid()
    plt.show()

if __name__ == "__main__":
    timespam = {
        'init': {'day': 21,'month': 8,'year': 2021,'hour': 0,'minute': 0,'second': 0},
        'end': {'day': 21,'month': 9,'year': 2021,'hour': 0,'minute': 0,'second': 0}
    }

    hls_pair = get_data_from_archiver(HLS_PVS, timespam)
    hls_pair['diff'] = hls_pair.iloc[:,0] - hls_pair.iloc[:,1]

    rf = get_data_from_archiver(RF_PV, timespam)
    rf = DataUtils.filter_and_save_dataframe(rf)

    plot_timeseries({"hls": [hls_pair.index, hls_pair.loc[:,'diff'],],
                     'rf': [rf.index, rf.iloc[:,0]]})
    