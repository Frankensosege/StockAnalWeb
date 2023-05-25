import pandas as pd
import numpy as np
from Utilities.DBManager import DBman

COLUMNS_TRAINING_DATA = [
    'date', 'open', 'high', 'low', 'close', 'gov_trade', 'for_trade',
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_boll_high', 'close_boll_high',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
]
def load_data(item_code, date_from, date_to):
    al_conn = DBman().get_alchmy_con("REPEATABLE READ")
    sql = "SELECT date, open, high, low, close, diff, volume, 'gov_trade', 'for_trade' "\
          f"FROM daily_price WHERE code = {item_code}" \
          f"WHERE date >= {date_from} AND date <= {date_to}" \
          "ORDER BY date DESC "
    result_df = pd.read_sql(sql, al_conn)
    result_df = preprocess(result_df)

    training_data = result_df[COLUMNS_TRAINING_DATA]

    return training_data.values


def preprocess(data):
    windows = [5, 10, 20, 60, 120]

    for window in windows:
        data[f'close_ma{window}'] = data['close'].rolling(window).mean()
        data[f'volume_ma{window}'] = data['volume'].rolling(window).mean()
        if window==20:
            data[f'close_boll_low'] = data[f'close_ma{window}'] - (data['close'].rolling(window).std() *2)
            data[f'close_boll_high'] = data[f'close_ma{window}'] + (data['close'].rolling(window).std() * 2)
        data[f'close_ma{window}_ratio'] = (data['close'] - data[f'close_ma{window}']) / data[f'close_ma{window}']
        data[f'volume_ma{window}_ratio'] = (data['volume'] - data[f'volume_ma{window}']) / data[f'volume_ma{window}']

    data['open_lastclose_ratio'] = np.zeros(len(data))
    data.loc[1:, 'open_lastclose_ratio'] = (data['open'][1:].values - data['close'][:-1].values) / data['close'][:-1].values
    data['high_close_ratio'] = (data['high'].values - data['close'].values) / data['close'].values
    data['low_close_ratio'] = (data['low'].values - data['close'].values) / data['close'].values
    data['close_lastclose_ratio'] = np.zeros(len(data))
    data.loc[1:, 'close_lastclose_ratio'] = (data['close'][1:].values - data['close'][:-1].values) / data['close'][:-1].values
    data['volume_lastvolume_ratio'] = np.zeros(len(data))
    data.loc[1:, 'volume_lastvolume_ratio'] = (
            (data['volume'][1:].values - data['volume'][:-1].values)
            / data['volume'][:-1].replace(to_replace=0, method='ffill') \
            .replace(to_replace=0, method='bfill').values
    )

    return data