from WebCrawler.StockData import anlDataMng
import pandas as pd
from Utilities.UsrLogger import stockLogger as sl
import json, calendar
from datetime import datetime
from threading import Timer
from Utilities.DBManager import DBman
from Investar.StockMarketDB import MarketDB

class DBUpdater:
    codes = {}
    def __init__(self):
        """생성자 : DB 연결 및 종목코드 딕셔너리 생성"""
        self.dbm = DBman()
        self.conn = self.dbm.get_connection()
        self.logger = sl(__name__).get_logger()

    def __del__(self):
        """소멸자 : DB 연결 해제"""
        # self.conn.rollback()
        # self.conn.close()

    def update_comp_info(self):
        self.logger.info('update_comp_info : DB에 저장된 company_info의 종목 정보를 딕셔너리에 저장')
        sd = anlDataMng()

        mkdb = MarketDB(self.dbm, self.logger)
        df = mkdb.get_comp_info()
        # df = MarketDB().get_comp_info()

        for idx in range(len(df)):
            self.codes[df['code'].values[idx]] = df['company'].values[idx]

        """종목코드를 company_info 테이블에 업데이트한 후 딕셔너리에 저장"""
        krx = pd.DataFrame()
        krx = sd.getItemList()
        today = datetime.today().strftime('%Y-%m-%d')

        try:
            with self.conn.cursor() as cur:
                """가장 최근 company_info update 일자"""
                sql = "SELECT max(last_update) FROM company_info"
                cur.execute(sql)
                rs = cur.fetchone()

                if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:
                    self.logger.info('update_comp_info : Start INSERT company information 가장 최근 company_info update 일자가 오늘 보다 작거나 처음 수행한 경우')
                    for idx in range(len(krx)):
                        code = krx.code.values[idx]
                        company = krx.company.values[idx]
                        sql = f"WITH upsert AS "\
                              f"(UPDATE company_info "\
                              f" SET company = '{company}', "\
                              f"     last_update = '{today}' "\
                              f" WHERE code = '{code}' "\
                              f" RETURNING * ) "\
                              f"INSERT INTO company_info (code, company, last_update) "\
                              f"SELECT '{code}', '{company}', '{today}' " \
                              f"WHERE NOT EXISTS (SELECT * FROM upsert);"
                        self.logger.info(f'update_comp_info : {sql}')
                        cur.execute(sql)
                        self.codes[code] = company
                    self.conn.commit()
                    self.logger.info('update_comp_info : End INSERT company information')

        except Exception as e:
            self.conn.rollback()
            self.logger.info('update_comp_info : ' +  str(e))


    def replace_price_naver(self, df, num, code, company):
        """네이버 금융에서 주식시세를 읽어 DB에 replace"""
        try:
            with self.conn.cursor() as cur:
                for r in df.itertuples():
                    self.logger.info('replace_price_naver: code:{}, name:{}, price_date{}'.format(code, company, r.date))
                    sql = f"WITH upsert AS "\
                          f"(UPDATE daily_price "\
                          f" SET open = {r.open}, "\
                          f"     high = {r.high}, "\
                          f"     low = {r.low}, "\
                          f"     close = {r.close}, "\
                          f"     diff = {r.diff}, "\
                          f"     volume = {r.volume} "\
                          f" WHERE code = '{code}' "\
                          f" AND   date = '{r.date}' "\
                          f" RETURNING * ) "\
                          f"INSERT INTO daily_price (code, date, open, high, low, close, diff, volume) "\
                          f"SELECT '{code}', '{r.date}', {r.open}, {r.high}, {r.low}, {r.close}, {r.diff}, {r.volume} " \
                          f"WHERE NOT EXISTS (SELECT * FROM upsert);"
                    cur.execute(sql)
                print(sql)
                self.conn.commit()
                self.logger.info('replace_price_naver : End update daily price #{:04d} {}:{}'.format(num+1, code, company))

        except Exception as e:
            self.conn.rollback()
            self.logger.info('replace_price_naver :' + str(e))



    def update_daily_price(self, pages_to_fetch):
        """네이버 금융에서 주식시세를 읽어 DB에 update"""

        sd = anlDataMng()
        for idx, code in enumerate(self.codes):
            df = sd.getDailyPriceNaver(code, self.codes[code], pages_to_fetch)
            if df is None:
                continue

            self.replace_price_naver(df, idx, code, self.codes[code])

    def get_company_name(self, code):
        """company_info 테이블로 부터 회사(법인)명을 가져온다"""
        sql = f"SELECT company FROM company_info WHRER ={code}"
        try:
            rs = pd.read_sql(sql, self.conn)
        except Exception as e:
            self.conn.rollback()
            self.logger.info('get_company_name : ', e)
            return None

        return rs[0]

    def execute_daily(self):
        """실행 즉시 및 매일 오후 5시에 daily_price 테이블 update"""
        self.logger.info('execute_daily : start-----')
        self.update_comp_info()
        try:
            with open('config.jason', 'r') as in_file:
                config = json.load(in_file)
                pages_to_fetch = config['pages_to_fetch']
        except FileNotFoundError:
            with open('config.jason', 'w') as out_file:
                pages_to_fetch = 100
                config = {'pages_to_fetch': 1}
                json.dump(config, out_file)

        self.update_daily_price(pages_to_fetch)

        tmnow = datetime.now()
        lastday = calendar.monthrange(tmnow.year, tmnow.month)[1]
        if tmnow.month == 12 and tmnow.day == lastday:
            tmnext = tmnow.replace(year=tmnow.year+1, month=1, day=1, hour=17, minute=0, second=0)
        elif tmnow.day == lastday:
            tmnext = tmnow.replace( month=tmnow.month+1, day=1, hour=17, minute=0, second=0)
        else:
            tmnext = tmnow.replace(day=tmnow.day+1, hour=17, minute=0, second=0)
        tmdiff = tmnext - tmnow
        secs = tmdiff.seconds

        t = Timer(secs, self.execute_daily)
        self.logger.info('execute_daily : Waiting for next update ({})'.format(tmnext.strftime('%y-%m-%d %H:%M')))
        t.start()


#if __name__ == '__main__':
#    print('aaaaaa')
#    dbu = DBUpdater()
#    dbu.execute_daily()