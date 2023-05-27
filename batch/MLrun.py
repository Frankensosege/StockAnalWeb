import logging
import os
import sys
from datetime import datetime
from Utilities.comUtilities import get_property
from Utilities.TrainModel import MLStockRNN
import pandas as pd
from Utilities.DBManager import DBman

def run():
    to_date = datetime.today().strftime('%Y-%m-%d')
    output_name = to_date + '_learning'
    # 로그 기록 설정
    log_path = os.path.join(get_property('LOG', 'fileLoc'), f'{output_name}.log')
    if os.path.exists(log_path):
        os.remove(log_path)
    logging.basicConfig(format='%(message)s')
    logger = logging.getLogger(get_property('LOG', 'ML_LOGGER_NAME'))
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename=log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    # logger.info(params)

    sql = f"SELECT item_code, start_dt, end_dt FROM learning_items WHERE schedule_dt = '{to_date}'"
    al_conn = DBman().get_alchmy_con("REPEATABLE READ")
    result_df = pd.read_sql(sql, al_conn)
    for idx, r in result_df.iterrows():
        logger.info(sql)
        model = MLStockRNN(r.item_code)
        model.train_model(r.start_dt, r.end_dt)

