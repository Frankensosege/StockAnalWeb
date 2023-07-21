import pandas as pd
from Utilities.UsrLogger import stockLogger as sl
from Utilities.DBManager import DBman
from datetime import datetime, timedelta
from Utilities.StockAnalExceptions import AnalException
from WebCrawler.StockData import getDailyPriceNaver, get_dart_fss

class MarketDB:
    def __init__(self):
        self.dbm = DBman()
        # self.logger = sl(__name__).get_logger()

    # def __del__(self):
    #     """소멸자 : DB 연결 해제"""
    #     self.conn.close()

    def get_company_name(self, code):
        """company_info 테이블로 부터 회사(법인)명을 가져온다"""
        sql = f"SELECT company FROM company_info WHRER ={code}"

        df = self.dbm.excute_alconn('get_company_name', sql)
        return df.iloc[0, 0]

    def replace_daily_price(self, row, code):
        """네이버 금융에서 주식시세를 읽어 DB에 replace"""
        # try:
        #     conn = self.dbm.get_connection()
        #     with conn.cursor() as cur:
        #         for r in df.itertuples():
        dbNm = self.dbm.get_db_nm()
        # sl(__name__).get_logger().info('replace_price_naver: code:{}, name:{}, price_date:{}'.format(code, company, row.date))
        if dbNm == 'mysql':
            # MySQL용 Merge
            sql = f"INSERT INTO daily_price (code, date, open, high, low, close, diff, volume, gov_trade, for_trade) " \
                  f"VALUES ('{code}', '{row.date}', {row.open}, {row.high}, {row.low}, {row.close}, {row.differ}, {row.volume}, {row.gov_trade}, {row.for_trade}) " \
                  f"ON DUPLICATE KEY " \
                  f"UPDATE open = {row.open}, high = {row.high}, low = {row.low}, close = {row.close}, diff = {row.differ}, volume = {row.volume}, gov_trade={row.gov_trade}, for_trade={row.for_trade}; "
        elif dbNm == 'postgresql':
            # postgreSQL 용 Merge 문
            sql = f"WITH upsert AS "\
                  f"(UPDATE daily_price "\
                  f" SET open = {row.open}, "\
                  f"     high = {row.high}, "\
                  f"     low = {row.low}, "\
                  f"     close = {row.close}, "\
                  f"     diff = {row.diff}, "\
                  f"     volume = {row.volume}, "\
                  f"     gov_trade={row.gov_trade}, " \
                  f"     for_trade={row.for_trade}" \
                  f" WHERE code = '{code}' "\
                  f" AND   date = '{row.date}' "\
                  f" RETURNING * ) "\
                  f"INSERT INTO daily_price (code, date, open, high, low, close, diff, volume, gov_trade, for_trade) "\
                  f"SELECT '{code}', '{row.date}', {row.open}, {row.high}, {row.low}, {row.close}, {row.differ}, {row.volume}, {row.gov_trade}, {row.for_trade} " \
                  f"WHERE NOT EXISTS (SELECT * FROM upsert);"
        #             cur.execute(sql)
        #             if not r.Index % 100:
        #                 conn.commit()
        #         conn.commit()
        #
        #
        # except Exception as e:
        #     conn.rollback()
        #     sl(__name__).get_logger().info('replace_price_naver :' + str(e))
        ret = self.dbm.excuteSQL('replace_daily_price', sql, True)

        return ret

    def get_laste_upate_comp(self):
        sql = "SELECT max(last_update) FROM company_info"
        df = self.dbm.excute_alconn('get_laste_upate_comp', sql)
        return df.iloc[0, 0]

    def update_comp_info(self, krx, today):
        # today = datetime.today().strftime('%Y-%m-%d')

        # try:
        #     conn = self.dbm.get_connection()
        #     with conn.cursor() as cur:
        #         """가장 최근 company_info update 일자"""
        #         sql = "SELECT max(last_update) FROM company_info"
        #         cur.execute(sql)
        #         rs = cur.fetchone()

                # if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:

        dbNm = self.dbm.get_db_nm()
        # for idx, r in krx.iterrows():
        if dbNm == 'mysql':
            # MySQL용 Merge
            sql = f"INSERT INTO company_info (code, company, last_update) " \
                  f"VALUES ('{krx.code}', '{krx.company}', '{today}') " \
                  f"ON DUPLICATE KEY " \
                  f"UPDATE company = '{krx.company}', last_update = '{today}'; "
        elif dbNm == 'postgresql':
            # postgreSQL 용 Merge 문
            sql = f"WITH upsert AS "\
                  f"(UPDATE company_info "\
                  f" SET company = '{krx.company}', "\
                  f"     last_update = '{today}' "\
                  f" WHERE code = '{krx.code}' "\
                  f" RETURNING * ) "\
                  f"INSERT INTO company_info (code, company, last_update) "\
                  f"SELECT '{krx.code}', '{krx.company}', '{today}' " \
                  f"WHERE NOT EXISTS (SELECT * FROM upsert);"

        ret = self.dbm.excuteSQL('update_comp_info', sql, True)

        return ret


    def get_comp_info(self, item_code=None, start=0, ret_items=0):
        dbNm = self.dbm.get_db_nm()
        if item_code is None:
            if ret_items == 0:
                sql = "SELECT * FROM company_info ORDER BY company "
            else:
                if dbNm == 'mysql':
                    sql = f"SELECT * FROM company_info ORDER BY company LIMIT {start}, {ret_items} "
                elif dbNm == 'postgresql':
                    sql = f"SELECT * FROM company_info ORDER BY company LIMIT {ret_items} OFFSET {start}  "
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
        dbNm = self.dbm.get_db_nm()
        if not user_id is None:
            sql = f"SELECT code, company FROM invest_items WHERE user_id = '{user_id}'"
        else:
            if ret_items==0:
                sql = f"SELECT DISTINCT code, company FROM invest_items ORDER BY company"
            else:
                if dbNm == 'mysql':
                    sql = f"SELECT DISTINCT code, company FROM invest_items ORDER BY company LIMIT {start}, {ret_items}"
                elif dbNm == 'postgresql':
                    sql = f"SELECT DISTINCT code, company FROM invest_items ORDER BY company LIMIT {ret_items} OFFSET {start}"

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

        sql = f"SELECT COM.code, COM.company, PRC.date, PRC.open, PRC.high, PRC.low, PRC.close, PRC.diff, PRC.volume, PRC.gov_trade, PRC.for_trade "\
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
            if len(items) <= 0:
                return None

            for item in items:
                code, company = item.split(':')
                sql = f'INSERT INTO invest_items (user_id, code, company) VALUES ("{user_id}", "{code.strip()}", "{company.strip()}")'
                ret = self.dbm.excute_alcon_CUD('create_invitem_list(insert)', sql)
                if ret is None:
                    return "투자종목 저장에 실패 했습니다."
        else:
            return "투자종목 삭제에 실패 했습니다."
        return None

    def update_daily_price(self, start_date, items):
        # sd = anlDataMng()
        dbNm = self.dbm.get_db_nm()
        for item in items:
            code, company = item.split(':')
            df = getDailyPriceNaver(code.strip(), company.strip(), start_date=start_date)

            if df is None:
                continue

            for r in df.itertuples():
                if dbNm == 'mysql':
                    # MySQL용 Merge
                    sql = f"INSERT INTO daily_price (code, date, open, high, low, close, diff, volume, gov_trade, for_trade) " \
                          f"VALUES ('{code}', '{r.date}', {r.open}, {r.high}, {r.low}, {r.close}, {r.differ}, {r.volume}, {r.gov_trade}, {r.for_trade}) " \
                          f"ON DUPLICATE KEY " \
                          f"UPDATE open = '{r.open}', high = {r.high}, low = {r.low}, close = {r.close}, diff = {r.differ}, volume = {r.volume}, gov_trade = {r.gov_trade}, for_trade = {r.for_trade}; "
                elif dbNm == 'postgresql':
                    # postgreSQL 용 Merge 문
                    sql = f"WITH upsert AS "\
                          f"(UPDATE daily_price "\
                          f" SET open = '{r.open}', high = {r.high}, low = {r.low}, close = {r.close}, diff = {r.differ}, volume = {r.volume}, gov_trade = {r.gov_trade}, for_trade = {r.for_trade} "\
                          f" WHERE code = '{code}' AND date = '{r.date}' "\
                          f" RETURNING * ) "\
                          f"INSERT INTO daily_price (ccode, date, open, high, low, close, diff, volume, gov_trade, for_trade) "\
                          f"SELECT '{code}', '{r.date}', {r.open}, {r.high}, {r.low}, {r.close}, {r.differ}, {r.volume}, {r.gov_trade}, {r.for_trade}) " \
                          f"WHERE NOT EXISTS (SELECT * FROM upsert);"

                # if r.Index % 200 == 0 or r == (len(df) - 1):
                #     is_commit = True
                # else:
                #     is_commit= False
                ret = self.dbm.excuteSQL('update_daily_price', sql, True)

                if ret is None:
                    return False
        return True

    def update_item_fss(self, start_date, fs_sheet, items):
        cnt = 0
        dbNm = self.dbm.get_db_nm()
        for item in items:
            code, company = item.split(':')
            start_date = start_date.replace('-', '')
            dict = get_dart_fss(code, start_date, fs_sheet)

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
                        dt_st, dt_en = col.split('-')

                    amt_df['amount'] = data_df[col]

                    for idx, r in amt_df.iterrows():
                        cnt += 1

                        if dbNm == 'mysql':
                            # MySQL용 Merge
                            sql = f"INSERT INTO item_fss (code, fss_code, date_start, date_end, account_nm, amount) " \
                                  f"VALUES ('{code}', '{fss_nm}', '{dt_st}', '{dt_en}','{r.account}', {r.amount}) " \
                                  f"ON DUPLICATE KEY UPDATE amount = {r.amount};"
                        elif dbNm == 'postgresql':
                            # postgreSQL 용 Merge 문
                            sql = f"WITH upsert AS " \
                                  f"(UPDATE item_fss " \
                                  f" SET amount = {r.amount} " \
                                  f" WHERE code = '{code}' " \
                                  f" AND fss_code = '{fss_nm}' " \
                                  f" AND date_start = '{dt_st}' " \
                                  f" AND date_end = '{dt_en}' " \
                                  f" AND account_nm = '{r.account}' "\
                                  f" RETURNING * ) " \
                                  f"INSERT INTO item_fss (code, fss_code, date_start, date_end, account_nm, amount) " \
                                  f"SELECT '{code}', '{r.date}', {r.open}, {r.high}, {r.low}, {r.close}, {r.diff}, {r.volume} " \
                                  f"WHERE NOT EXISTS (SELECT * FROM upsert);"
                        # if cnt % 200 == 0 or idx == (len(amt_df)-1):
                        #     is_commit = True
                        # else:
                        #     is_commit = False
                        ret = self.dbm.excuteSQL('update_item_fss', sql, True)

    def create_learn_schedule(self, start_date, end_date, items):
        dbNm = self.dbm.get_db_nm()
        for item in items:
            code, company = item.split(':')

            if dbNm == 'mysql':
                # MySQL용 Merge
                sql = f"INSERT INTO learning_items (schedule_dt, item_code, start_dt, end_dt) " \
                      f"VALUES (CURDATE(), '{code}', '{start_date}', '{end_date}') " \
                      f"ON DUPLICATE KEY UPDATE start_dt = '{start_date}', end_dt = '{end_date}';"
            elif dbNm == 'postgresql':
                # postgreSQL 용 Merge 문
                sql = f"WITH upsert AS " \
                      f"(UPDATE learning_items " \
                      f" SET amount = start_dt = '{start_date}', end_dt = '{end_date}' " \
                      f" WHERE schedule_dt = CURDATE() " \
                      f" AND item_code = '{code}' " \
                      f" RETURNING * ) " \
                      f"INSERT INTO item_fss (schedule_dt, item_code, start_dt, end_dt) " \
                      f"SELECT current_date, '{code}', '{start_date}', '{end_date}' " \
                      f"WHERE NOT EXISTS (SELECT * FROM upsert);"


            ret = self.dbm.excuteSQL('create_learn_schedule', sql, True)

            if ret is None:
                return False
        return True

    def get_total_tool_count(self, user_id=None):
        if user_id is None:
            sql = 'SELECT COUNT(*) cnt FROM anal_tools'
        else:
            pass
            # sql = f'SELECT COUNT(*) cnt FROM invest_items where userid = "{user_id}"'
        df = self.dbm.excute_alconn('get_total_tool_count', sql)
        return df.iloc[0, 0]

    def get_tools(self, start=0, ret_items=0, user_id=None, tool_id=None):
        if user_id is None:
            if tool_id is None:
                sql = f'SELECT tool_id, tool_nm, tool_method, img_prefix FROM anal_tools LIMIT {start}, {ret_items} '
            else:
                sql = f"SELECT tool_id, tool_nm, tool_method, img_prefix FROM anal_tools WHERE tool_id = '{tool_id}' "
        else:
            pass
            # sql = f'SELECT COUNT(*) cnt FROM invest_items where userid = "{user_id}"'
        df = self.dbm.excute_alconn('get_tools', sql)
        return df

    def save_tool(self, tool_data):
        # sd = anlDataMng()
        tool_id = tool_data['tool_id']
        tool_nm = tool_data['tool_nm']
        tool_method = tool_data['tool_method']
        img_prefix = tool_data['img_prefix']
        dbNm = self.dbm.get_db_nm()
        if dbNm == 'mysql':
            # MySQL용 Merge
            sql = f"INSERT INTO anal_tools (tool_id, tool_nm, tool_method, img_prefix) " \
                  f"VALUES ('{tool_id}', '{tool_nm}', '{tool_method}', '{img_prefix}') " \
                  f"ON DUPLICATE KEY " \
                  f"UPDATE tool_nm = '{tool_nm}', tool_method = '{tool_method}', img_prefix = '{img_prefix}'; "
        elif dbNm == 'postgresql':
            # postgreSQL 용 Merge 문
            sql = f"WITH upsert AS "\
                  f"(UPDATE daily_price "\
                  f" SET tool_nm = '{tool_nm}', tool_method = '{tool_method}', img_prefix = '{img_prefix}' "\
                  f" WHERE tool_id = '{tool_id}' "\
                  f" RETURNING * ) "\
                  f"INSERT INTO anal_tools (tool_id, tool_nm, tool_method, img_prefix) "\
                  f"SELECT '{tool_id}', '{tool_nm}', '{tool_method}', '{img_prefix}') " \
                  f"WHERE NOT EXISTS (SELECT * FROM upsert);"

        ret = self.dbm.excuteSQL('update_daily_price', sql, True)

        if ret is None:
            return False
        return True

    def delete_tool(self, tool_id):
        sql = f"DELETE FROM anal_tools WHERE tool_id = '{tool_id}' "
        ret = self.dbm.excuteSQL('update_daily_price', sql, True)

        if ret is None:
            return False
        return True

    def get_hloc(self, item_code, date_from=None, date_to=None, is_train=True):
        if is_train:
            sql = "SELECT date, open, high, low, close, diff, volume, gov_trade, for_trade " \
                  f"FROM daily_price WHERE code = '{item_code}'" \
                  f"AND date BETWEEN '{date_from}' AND '{date_to}' " \
                  "ORDER BY date "
        else:
            sql = "SELECT date, open, high, low, close, diff, volume, gov_trade, for_trade " \
                  "FROM (SELECT row_number() over(order by date desc) as num, " \
                  "             date, open, high, low, close, diff, volume, gov_trade, for_trade  " \
                  "      FROM daily_price  " \
                  f"     WHERE  code = '{item_code}' " \
                  f"     AND date <= curdate() " \
                  "      ) prc " \
                  "WHERE prc.num <= 125 " \
                  "ORDER BY date "

        df = self.dbm.excute_alconn('get_tools', sql)
        return df