import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

ARCHIVER_URL = 'http://10.0.38.42/retrieval/data/getData.json'

class Archiver:
    @staticmethod
    async def fetch_pv(session, pv, time_from, time_to, is_optimized, mean_minutes):
        pv_query = f'mean_{int(60*mean_minutes)}({pv})' if is_optimized else pv
        query = {'pv': pv_query, 'from': time_from, 'to': time_to}
        
        async with session.get(ARCHIVER_URL, params=query) as response:
            response_as_json = await response.json()
            return response_as_json

    @staticmethod
    async def fetch_multiple_pvs(pvs: list, time_from: str, time_to: str, isOptimized: bool=False, mean_minutes: int=0):
        async with aiohttp.ClientSession() as session:
            data = await asyncio.gather(*[Archiver.fetch_pv(session, pv, time_from, time_to, isOptimized, mean_minutes) for pv in pvs])
            return data

    @staticmethod
    async def request_data(pvs: list, timespam: dict, aquisition_period_in_minutes: int) -> pd.DataFrame:
        datetime_init = datetime(timespam['init']['year'], timespam['init']["month"], timespam['init']["day"], timespam['init']["hour"], timespam['init']["minute"], timespam['init']["second"]) + timedelta(hours=3)
        datetime_end = datetime(timespam['end']['year'], timespam['end']["month"], timespam['end']["day"], timespam['end']["hour"], timespam['end']["minute"], timespam['end']["second"]) + timedelta(hours=3)

        dt_init_formatted = datetime_init.isoformat(timespec='milliseconds') + 'Z'
        dt_end_formatted = datetime_end.isoformat(timespec='milliseconds') + 'Z'

        timespam = (dt_init_formatted, dt_end_formatted)

        print("fetching data...")

        try:
            # retrieving raw data from Archiver
            json_data = await Archiver.fetch_multiple_pvs(pvs, timespam[0], timespam[1], True, aquisition_period_in_minutes)

            # mapping pv's values
            data = [np.array(list(map(lambda i: i['val'], serie))) for serie in map(lambda j: j[0]['data'], json_data)]
            # mapping timestamps
            time_fmt = list(map(lambda data: datetime.fromtimestamp(data['secs']), json_data[0][0]['data']))

            # creating pandas dataframe object
            d = {'datetime': time_fmt}
            for l_data, name in zip(data, pvs):
                d[name] = l_data
            data = pd.DataFrame(data=d)
            
            data.reset_index(drop=True, inplace=True)
            data = data.set_index('datetime')
            print('data fetched!')
            return data

        except IndexError:
            print('Fetching data failed.')
            return
