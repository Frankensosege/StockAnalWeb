import pandas as pd
from Utilities.UsrLogger import stockLogger as sl
from Utilities.DBManager import DBman
from datetime import datetime, timedelta
from Utilities.StockAnalExceptions import AnalException

class MarketDB:
    def __init__(self):
        self.dbm = DBman()
        # self.conn = self.dbm.get_connection()
        self.logger = sl(__name__).get_logger()

    # def __del__(self):
    #     """소멸자 : DB 연결 해제"""
    #     self.conn.close()

    def get_comp_info(self, item_code=None, start=0, ret_items=0):
        if item_code is None:
            if ret_items == 0:
                sql = "SELECT * FROM company_info"
            else:
                sql = f"SELECT * FROM company_info LIMIT {start}, {ret_items}"
        else:
            sql = f"SELECT * FROM company_info WHERE code = '{item_code}'"

        df = self.dbm.excute_alconn('get_comp_info', sql)

        return df

    def get_invest_items(self, user_id=None):
        if not user_id is None:
            sql = f"SELECT code, company FROM invest_item WHERE id = '{user_id}'"
        else:
            sql = "SELECT DISTINCT code, company FROM invest_item"

        df = self.dbm.excute_alconn('get_invest_items', sql)

        return df

    def get_total_item_count(self):
        sql = 'SELECT count(*) as cnt FROM company_info'
        df = self.dbm.excute_alconn('get_total_item_count', sql)
        return df.iloc[0, 0]

    def get_daily_price(self, item_code, start_day=None, end_day=None):
        if start_day is None:
            one_year_ago = datetime.today() - timedelta(days=365)
            start_day = one_year_ago.strftime('%Y-%m-%d')

        if end_day is None:
            end_day = datetime.today().strftime('%Y-%m-%d')

        if item_code is None:
            raise AnalException('종목 코드는 필수 입니다.')

        sql = f"SELECT COM.code, COM.company, PRC.date, PRC.open, PRC.high, PRC.low, PRC.close, PRC.diff, PRC.volume "\
              f"FROM company_info COM, daily_price PRC"\
              f"WHERE COM.code = PRC.code" \
              f"AND COM.code = '{item_code}' " \
              f"AND PRC.date >= '{start_day}' " \
              f"AND PRC.date <= '{end_day}' "

        try:
            al_conn = self.dbm.get_alchmy_con("REPEATABLE READ")
            with al_conn.begin() as al_conn:
                sql = self.dbm.get_alchemy_query(sql)
                df = pd.read_sql(sql, al_conn)
        except AnalException as e:
            self.logger.info('get_daily_price : ' + str(e))
            return None
        except Exception as e:
            self.logger.info('get_daily_price : ' + str(e))
            return None

        return df
