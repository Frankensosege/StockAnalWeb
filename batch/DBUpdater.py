from WebCrawler.StockData import getItemList, getDailyPriceNaver
import pandas as pd
from Utilities.UsrLogger import stockLogger as sl
from datetime import datetime
# from Utilities.DBManager import DBman
from Utilities.StockMarketDB import MarketDB
from Utilities.comUtilities import get_property

class DBUpdater:
    codes = pd.DataFrame()
    def __init__(self):
        """생성자 : DB 연결 및 종목코드 딕셔너리 생성"""
        # self.dbm = DBman()
        # self.cu = commonUtilities('./config.ini')

    def __del__(self):
        """소멸자 : DB 연결 해제"""
        # self.conn.rollback()
        # self.conn.close()

    def update_comp_info(self):
        # sl(__name__).get_logger().info('update_comp_info : DB에 저장된 company_info의 종목 정보를 딕셔너리에 저장')
        # sd = anlDataMng()

        mkdb = MarketDB()

        today = datetime.today().strftime('%Y-%m-%d')
        lst_dt = mkdb.get_laste_upate_comp()

        sl(__name__).get_logger().info('update_comp_info : Start INSERT company information 가장 최근 company_info update 일자가 오늘 보다 작거나 처음 수행한 경우')

        self.codes = getItemList()
        if lst_dt == None or lst_dt.strftime('%Y-%m-%d') < today:
            for idx, r in self.codes.iterrows():
                mkdb.update_comp_info(r, today)
        # today = datetime.today().strftime('%Y-%m-%d')
        #
        # try:
        #     conn = self.dbm.get_connection()
        #     with conn.cursor() as cur:
        #         """가장 최근 company_info update 일자"""
        #         sql = "SELECT max(last_update) FROM company_info"
        #         cur.execute(sql)
        #         rs = cur.fetchone()
        #
        #         if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:
        #             sl(__name__).get_logger().info('update_comp_info : Start INSERT company information 가장 최근 company_info update 일자가 오늘 보다 작거나 처음 수행한 경우')
        #             for idx in range(len(krx)):
        #                 code = krx.code.values[idx]
        #                 company = krx.company.values[idx]
        #
        #                 # MySQL용 Merge
        #                 sql = f"INSERT INTO company_info (code, company, last_update) " \
        #                       f"VALUES ('{code}', '{company}', '{today}') " \
        #                       f"ON DUPLICATE KEY " \
        #                       f"UPDATE company = '{company}', last_update = '{today}'; "
        #
        #
        #                 # postgreSQL 용 Merge 문
        #                 # sql = f"WITH upsert AS "\
        #                 #       f"(UPDATE company_info "\
        #                 #       f" SET company = '{company}', "\
        #                 #       f"     last_update = '{today}' "\
        #                 #       f" WHERE code = '{code}' "\
        #                 #       f" RETURNING * ) "\
        #                 #       f"INSERT INTO company_info (code, company, last_update) "\
        #                 #       f"SELECT '{code}', '{company}', '{today}' " \
        #                 #       f"WHERE NOT EXISTS (SELECT * FROM upsert);"
        #
        #
        #                 cur.execute(sql)
        #                 self.codes[code] = company
        #             conn.commit()
        #             sl(__name__).get_logger().info('update_comp_info : End INSERT company information')
        #
        # except Exception as e:
        #     conn.rollback()
        #     sl(__name__).get_logger().info('update_comp_info : ' +  str(e))
        sl(__name__).get_logger().info('update_comp_info : End INSERT company information')


    def update_daily_price(self, pages_to_fetch):
        """네이버 금융에서 주식시세를 읽어 DB에 update"""

        # sd = anlDataMng()
        mkdb = MarketDB()
        for idx, r in self.codes.iterrows():
            df = getDailyPriceNaver(r.code, r.company, pages_to_fetch=pages_to_fetch)
            if df is None:
                continue

            for idx, prc in df.iterrows():
                mkdb.replace_daily_price(prc, r.code)
        sl(__name__).get_logger().info('update_daily_price : End update daily price #{:04d} {}:{}'.format(idx + 1, r.code, r.company))


    # ## 초기 company 별 주가자료를 모두 가져 오도록 한다.
    # def update_all_price_company(self, code):
    #     sd = anlDataMng()
    #     mkdb = MarketDB()
    #     com_name = mkdb.get_company_name(code)
    #     df = sd.getDailyPriceNaver(code, com_name, 0)
    #     if df is None:
    #         return None
    #
    #     for idx, prc in df.iterrows():
    #         mkdb.replace_dily_price(prc, code, com_name)
    #         sl(__name__).get_logger().info(
    #             'update_all_price_company : End update daily price #{:04d} {}:{}'.format(idx + 1, r.code, r.company))
    #     return df.length()

    def execute_daily(self):
        """실행 즉시 및 매일 오후 5시에 daily_price 테이블 update"""
        # pages_to_fetch 가져올 일별 price(0 전체)
        pages_to_fetch = get_property('DPrice', 'pages_to_fetch')
        sl(__name__).get_logger().info('execute_daily : start-----')
        self.update_comp_info()
        self.update_daily_price(pages_to_fetch)

        # tmnow = datetime.now()
        # lastday = calendar.monthrange(tmnow.year, tmnow.month)[1]
        # if tmnow.month == 12 and tmnow.day == lastday:
        #     tmnext = tmnow.replace(year=tmnow.year+1, month=1, day=1, hour=17, minute=0, second=0)
        # elif tmnow.day == lastday:
        #     tmnext = tmnow.replace(month=tmnow.month+1, day=1, hour=17, minute=0, second=0)
        # else:
        #     tmnext = tmnow.replace(day=tmnow.day+1, hour=17, minute=0, second=0)
        # tmdiff = tmnext - tmnow
        # secs = tmdiff.seconds
        #
        # t = Timer(secs, self.execute_daily)   # 메일 스케쥴링
        # self.logger.info('execute_daily : Waiting for next update ({})'.format(tmnext.strftime('%y-%m-%d %H:%M')))
        # t.start()


#if __name__ == '__main__':
#    print('aaaaaa')
#    dbu = DBUpdater()
#    dbu.execute_daily()