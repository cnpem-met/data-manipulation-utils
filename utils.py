from scipy.signal import butter, filtfilt
from scipy.stats import pearsonr
from scipy.fft import rfftfreq, rfft
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from plot import PickPointsPlot

class MathUtils:

    @staticmethod
    def filter_timeserie(timeserie, min_period) -> np.array:
        T = 60 # in seconds
        filter_type = 'lowpass'
        filter_limit = 1/(3600*min_period)

        b, a = butter(4, filter_limit, filter_type, fs=1/T)
        filtered_data = filtfilt(b,a, timeserie)

        return filtered_data

    @staticmethod
    def calculate_correlation(serie1: list, serie2: list, corr_type: str = 'pearson'):
        if (corr_type == 'pearson'):
            corr, _ = pearsonr(serie1, serie2)
        elif (corr_type == 'cross'):
            # calculating time-based normalized cross-correlation
            s1 = (serie1 - np.mean(serie1))/(np.std(serie1)*len(serie1))
            s2 = (serie2 - np.mean(serie2))/(np.std(serie2))
            corr = np.correlate(s1, s2, mode='full')
            corr = max(corr)
        
        print(f'{corr_type} correlation: {corr:.4f}')
    
    @staticmethod
    def calculate_fft(timeserie: list, acq_period_in_seconds: float):
        series_length = len(timeserie)
        # creating frequency x axis data
        freq_raw = rfftfreq(series_length, acq_period_in_seconds)
        # calculating fft
        fft = rfft(timeserie)
        fft = np.abs(fft[1:])**2
        psd = 2/(series_length/2) * fft
        freq = np.array(freq_raw[1:])
        # converting x values from Hz to hours
        period = 1/freq/60/60
        return (period, psd)
    

class DataUtils:
    @staticmethod
    def filter_and_save_dataframe(df: pd.DataFrame, plot_output: bool = False, file_basename: str = "filtered_data") -> pd.DataFrame:
        """ filtering data from a DataFrame by selecting the outliers in the plot
            process: select outlier to exclude by circulating then with the mouse; after each selection
                     press enter to compute then and move to next outliers to exclude; once finished the 
                     selecting, just close the plot window and the filtered dataset will be saved in a
                     .xlsx format and shown in a new plot windows (if plot_output is True) """

        # x = rf.get_data().index.values
        y = df.iloc[:,0].values
        x = np.arange(0,len(y), 1)

        selected_points = PickPointsPlot.plot(x, y)
        index_selected = list(map(lambda p: int(p[0]), selected_points))

        # mask = np.ones(y.size, dtype=bool)
        # mask[index_selected] = False
        # y_filtered = y[mask]

        df.iloc[index_selected,0] = None
        # df = df[mask]

        if (plot_output):
            df.plot()
            plt.show()

        # df.to_excel(file_basename + '.xlsx')
        return df

    @staticmethod
    def load_datetime_series_from_excel(filepath) -> pd.DataFrame:
        data = pd.read_excel(filepath)
        # data.index = pd.DatetimeIndex([datetime.strptime(ts_str, "%d.%m.%y %H:%M") for ts_str in data['datetime']])
        # data.index = pd.DatetimeIndex([datetime.strptime(ts_str, "%Y-%m-%d %H:%M:$S") for ts_str in data['datetime']])
        data.index = pd.DatetimeIndex(data['datetime'])
        data.drop(columns=['datetime'], inplace=True)
        return data

    @staticmethod
    def filter_dataframes_mutually(df1: pd.DataFrame, df2: pd.DataFrame):
        """ select index (rows) that exists in both DataFrames and filter the rest of rows """
        intersection_idx = df1.index.intersection(df2.index)
        df1_filtered = df1.loc[intersection_idx, :]
        df2_filtered = df2.loc[intersection_idx, :]
        return df1_filtered, df2_filtered