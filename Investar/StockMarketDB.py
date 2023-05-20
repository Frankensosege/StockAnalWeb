import pandas as pd
from Utilities.UsrLogger import stockLogger as sl
from Utilities.DBManager import DBman
from datetime import datetime, timedelta
from Utilities.StockAnalExceptions import AnalException
from WebCrawler.StockData import anlDataMng

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
                sql = "SELECT * FROM company_info ORDER BY company "
            else:
                sql = f"SELECT * FROM company_info ORDER BY company LIMIT {start}, {ret_items} "
        else:
            sql = f"SELECT * FROM company_info WHERE code = '{item_code}'"

        df = self.dbm.excute_alconn('get_comp_info', sql)

        return df

    def get_total_invest_item_count(self, user_id=None):
        if user_id is None:
            sql = 'SELECT COUNT(*) cnt FROM (SELECT DISTINCT code, company FROM invest_items) inv'
        else:
            sql = f'SELECT COUNT(*) cnt FROM invest_items where userid = "{user_id}"'
        df = self.dbm.excute_alconn('get_total_invest_item_count', sql)
        return df.iloc[0, 0]

    def get_invest_items(self, user_id=None, start=0, ret_items=0):
        if not user_id is None:
            sql = f"SELECT code, company FROM invest_items WHERE user_id = '{user_id}'"
        else:
            if ret_items==0:
                sql = f"SELECT DISTINCT code, company FROM invest_items ORDER BY company"
            else:
                sql = f"SELECT DISTINCT code, company FROM invest_items ORDER BY company LIMIT {start}, {ret_items}"

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

    def create_invitem_list(self, user_id, items):
        sql = f'DELETE FROM invest_items WHERE user_id = "{user_id}"'
        ret = self.dbm.excute_alcon_CUD('create_invitem_list(delete)', sql)

        if ret is not None:
            for item in items:
                code, company = item.split()
                sql = f'INSERT INTO invest_items (user_id, code, company) VALUES ("{user_id}", "{code}", "{company}")'
                ret = self.dbm.excute_alcon_CUD('create_invitem_list(insert)', sql)
                if ret is None:
                    return "투자종목 저장에 실패 했습니다."
        else:
            return "투자종목 삭제에 실패 했습니다."
        return None

    def update_daily_price(self, start_date, items):
        sd = anlDataMng()
        for item in items:
            print(item)
            code, company = item.split()
            df = sd.getDailyPriceNaver(code, company, start_date=start_date)

            if df is None:
                continue

            for r in df.itertuples():
                # MySQL용 Merge
                sql = f"INSERT INTO daily_price (code, date, open, high, low, close, diff, volume) " \
                      f"VALUES ('{code}', '{r.date}', {r.open}, {r.high}, {r.low}, {r.close}, {r.diff}, {r.volume}) " \
                      f"ON DUPLICATE KEY " \
                      f"UPDATE open = '{r.open}', high = '{r.high}', low = '{r.low}', close = '{r.close}', diff = '{r.diff}', volume = '{r.volume}'; "

                # if r.Index % 200 == 0 or r == (len(df) - 1):
                #     is_commit = True
                # else:
                #     is_commit= False
                ret = self.dbm.excuteSQL('update_daily_price', sql, True)

                if ret is None:
                    return False
        return True

    def update_item_fss(self, start_date, fs_sheet, items):
        sd = anlDataMng()
        cnt = 0
        for item in items:
            code, company = item.split()
            start_date = start_date.replace('-', '')
            dict = sd.get_dart_fss(code, start_date, fs_sheet)

            if dict is None:
                continue

            for fss in dict:
                data_df = dict[fss]
                colums = data_df.columns

                amt_df=pd.DataFrame()
                for col in colums:
                    if col.lower()=='ko':
                        amt_df['account'] = data_df[col]
                        continue
                    if col.lower()=='en':
                        continue

                    _, fss_nm = fss.split('_')

                    if fss_nm=='bs':
                        dt_st, dt_en = col, col
                    else:
                        print('-------------------------------------')
                        print(col)
                        dt_st, dt_en = col.split('-')

                    amt_df['amount'] = data_df[col]

                    for idx, r in amt_df.iterrows():
                        cnt += 1

                        sql = f"INSERT INTO item_fss (code, fss_code, date_start, date_end, account_nm, amount) " \
                              f"VALUES ('{code}', '{fss_nm}', '{dt_st}', '{dt_en}','{r.account}', {r.amount}) " \
                              f"ON DUPLICATE KEY UPDATE amount = {r.amount};"

                        # if cnt % 200 == 0 or idx == (len(amt_df)-1):
                        #     is_commit = True
                        # else:
                        #     is_commit = False
                        ret = self.dbm.excuteSQL('update_item_fss', sql, True)




