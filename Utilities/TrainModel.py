from tensorflow.keras.layers import Input, LSTM, BatchNormalization, Dense
from tensorflow.keras.models import Model
from Utilities.StockMarketDB import MarketDB
from Utilities.comUtilities import get_property
from datetime import datetime, timedelta
import numpy as np
import os.path

COLUMNS_TRAINING_DATA = [
    'date', 'open', 'high', 'low', 'close', 'diff', 'volume', 'gov_trade', 'for_trade',
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_boll_low', 'close_boll_high',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',


'close_ma5', 'volume_ma5', 'close_ma10', 'volume_ma10', 'close_ma20',
       'volume_ma20', 'close_boll_low', 'close_ma60', 'volume_ma60',
       'close_ma120', 'volume_ma120'
]
def load_data(item_code, date_from=None, date_to=None, is_train=True):
    # al_conn = DBman().get_alchmy_con("REPEATABLE READ")
    # if is_train:
    #     sql = "SELECT date, open, high, low, close, diff, volume, gov_trade, for_trade "\
    #           f"FROM daily_price WHERE code = '{item_code}'" \
    #           f"AND date BETWEEN '{date_from}' AND '{date_to}' " \
    #           "ORDER BY date "
    # else:
    #     sql = "SELECT date, open, high, low, close, diff, volume, gov_trade, for_trade "\
    #           "FROM (SELECT row_number() over(order by date desc) as num, " \
    #           "             date, open, high, low, close, diff, volume, gov_trade, for_trade  " \
    #           "      FROM daily_price  " \
    #           f"     WHERE  code = '{item_code}' " \
    #           f"     AND date <= curdate() " \
    #           "      ) prc " \
    #           "WHERE prc.num <= 125 " \
    #           "ORDER BY date "

    # result_df = pd.read_sql(sql, al_conn)

    prepSQL = MarketDB()
    result_df = prepSQL.get_hloc(item_code, date_from=date_from, date_to=date_to, is_train=is_train)
    result_df = preprocess(result_df)

    training_data = result_df[COLUMNS_TRAINING_DATA]
    training_data = training_data.fillna(0)

    return training_data


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

def get_train_data(item_code, date_from, date_to, window_size, hold_ratio):
    to_dt = date_to + timedelta(days=5)

    if to_dt > datetime.today().date():
        raise Exception(f"학습 종료일은 {(datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d')} 보다 이전이 어야 합니다.")
    data_train = load_data(item_code, date_from, date_to)
    # print(data_train.columns)
    label = data_train[['close']]
    data_train.to_csv(get_property('DATA', 'base_dir') + get_property('DATA', 'modelpath') + 'train.csv')

    data_train.drop(['date'], axis=1, inplace=True)

    print(data_train.columns)
    print(len(data_train.columns))
    print(data_train)

    feature_list = []
    label_list = []
    for i in range(len(data_train) - window_size):
        feature_list.append((data_train.iloc[i:i+window_size])) # 5개의 데이터가 합쳐진다
        # print(label['close'][i+window_size], label['close'][i+window_size-1])
        close_amt = label['close'][i+window_size-1]
        hold_high = int(close_amt + (close_amt * hold_ratio))
        hold_low = int(close_amt - (close_amt * hold_ratio))
        if (label['close'][i+window_size]>label['close'][i+window_size-1]):
            label_list.append([0])
        elif (label['close'][i+window_size]<=hold_high and label['close'][i+window_size]>=hold_low):
            label_list.append([2])
        else:
            label_list.append([1])
        # label_list.append((label.iloc[i+window_size]))# 5개의 데이터에 6번째 데이터의 결과가 나온다, 즉 5개의 데이터로 6번째 데이터 예측
    return np.array(feature_list), np.array(label_list)


def get_pedict_sample(item_code, window_size):
    data = load_data(item_code, is_train=False)
    # data = preprocess(data)

    df_ret = data[len(data)-window_size:]
    df_ret.drop(['date'], axis=1, inplace=True)

    print(df_ret.columns)
    print(len(df_ret.columns))
    print(df_ret)

    return  np.array(df_ret)


class MLStockRNN:
    def __init__(self, item_code, window_size=5, hold_ratio=5):
        self.item_code = item_code
        self.file_nm = f'LSTM_weight_{item_code}.h5'
        self.file_path = get_property('DATA', 'base_dir') + get_property('DATA', 'modelpath') + self.file_nm
        self.window_size = window_size
        self.hold_ratio = hold_ratio

        try:
            if not os.path.exists(get_property('DATA', 'base_dir') + get_property('DATA', 'modelpath')):
                os.makedirs(get_property('DATA', 'base_dir') + get_property('DATA', 'modelpath'))
        except OSError:
            print("Error: Failed to create the directory.")

    def get_model(self, inp):
        output = LSTM(256, dropout=0.1, return_sequences=True,
                      kernel_initializer='random_normal', activation='tanh')(inp)
        output = BatchNormalization()(output)
        output = LSTM(128, dropout=0.1, return_sequences=True,
                      kernel_initializer='random_normal', activation='tanh')(output)
        output = BatchNormalization()(output)
        output = LSTM(64, dropout=0.1, return_sequences=True,
                      kernel_initializer='random_normal', activation='tanh')(output)
        output = BatchNormalization()(output)
        output = LSTM(32, dropout=0.1, kernel_initializer='random_normal', activation='tanh')(output)
        output = BatchNormalization()(output)
        output = Dense(3, activation='softmax')(output)
        return Model(inp, output)

    def save_weight(self,  model):
        model.save_weights(self.file_path)

    def train_model(self, date_from, date_to, use_trained_weight=False, save_model=True):
        x, y = get_train_data(self.item_code, date_from, date_to, self.window_size, self.hold_ratio)

        inp = Input((x.shape[1], x.shape[2]))
        model = self.get_model(inp)
        if use_trained_weight:
            if not os.path.isfile(self.file_path):
                raise Exception(self.file_path + "가중치 파일이 존재하지 하지 않습니다.")

            model.load_weights(self.file_path)


        # train data --> x, y
        loss = 0.
        print(model.summary())
        print(x.shape, y.shape)
        model.compile(loss='sparse_categorical_crossentropy', optimizer='adam')
        history = model.fit(x, y, epochs=100, verbose=False)
        loss += np.sum(history.history['loss'])
        if save_model:
            self.save_weight(model)
        return loss

    def predict(self):
        # 예측데이터 가져오기
        sample = get_pedict_sample(self.item_code, self.window_size)

        inp = Input((sample.shape[0], sample.shape[1]))

        model = self.get_model(inp)

        if not os.path.isfile(self.file_path):
            return None

        model.load_weights(self.file_path)

        # model = self.load_model_weght(model)
        # if model is None:
        #     raise Exception(self.file_path + "가중치 파일이 존재하지 하지 않습니다.")

        sample = np.expand_dims(sample, axis=0)
        pred = model.predict(sample)

        return pred





