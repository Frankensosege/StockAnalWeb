import pandas as pd
from bs4 import BeautifulSoup
import requests
from Utilities.comUtilities import commonUtilities
import mplfinance as mpf
from Utilities.UsrLogger import stockLogger as sl

class anlDataMng:
    def __init__(self):
        self.logger = sl(__name__).get_logger()
        self.cu = commonUtilities('./config.ini')

    def getItemList(self):
        #한국거래소 기업공시 체널에서 종목 목록 가져오기
        try:
            url = '{}{}{}'.format(self.cu.get_property('URLs', 'kind'),
                                    self.cu.get_property('URLs', 'kindItemPage'),
                                    '/corpList.do?method=download&searchType=13')
            print(url)
            df = pd.read_html(url)[0]
            df = df[['종목코드', '회사명']]
            df = df.rename(columns={'종목코드':'code', '회사명':'company'})
            df.code = df.code.map('{:06d}'.format)
        except Exception as e:
            self.logger.error("getItemList : " + e)
            return None

        return df

    def __getLastPageNaver(self, url):
        #네이버 금융에서 종목별 과거 주가가져오기
        lp_html = requests.get(url, headers={'User-agent':'Mozilla/5.0'}).text
        bs = BeautifulSoup(lp_html, 'lxml')
        pgrr = bs.find('td', class_=self.cu.get_property('ETC', 'naverLpageClass'))
        if pgrr == None:
            return None
        s = str(pgrr.a['href']).split('=')
        # print(s, s[-1])

        return s[-1]

    def getDailyPriceNaver(self, itemCode, company, pages_to_fetch):
        #Naver 종목별 시세 페이지
        try:
            url = self.cu.get_property('URLs', 'naverFinance')
            url = '{}{}?code={}'.format(url, self.cu.get_property('URLs', 'naverItmePrice'), itemCode)
            # Naver 종목별 시세 마지막 페이지 가져오기
            urlpage = '{}&page=1'.format(url)
            lastpg = self.__getLastPageNaver(urlpage)
            if lastpg == None:
                return None
            df = pd.DataFrame()
            pages = min(int(lastpg), pages_to_fetch)
            for page in range(1, pages + 1):
                prcUrl = '{}&page={}'.format(url, page)
                html = requests.get(prcUrl, headers={'User-agent': 'Mozilla/5.0'}).text

                df = df.append(pd.read_html(html, header=0)[0])
                self.logger.info("getItemList : Download {}:{} - Page {:04d} / {:04d}".format(itemCode, company, page, pages))

            df = df.rename(columns={'날짜':'date', '종가':'close', '전일비':'diff', '시가':'open', '고가':'high', '저가':'low', '거래량':'volume'})
            df['date'] = df['date'].replace('.', '-')
            df = df.dropna()
            df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)
            df = df[['date', 'open', 'high', 'low', 'close', 'diff', 'volume']]
        except Exception as e:
            self.logger.error("getDailyPriceNaver : " + str(e))
            return None

        return df

    def drawCandleChart(self, sdate, ldate, itemcode):
        #읽어온 데이터를 캔들 챠트로 출력한다.
        # to-do 1. Item 코드로 DB에서 데이터 읽어어와 pandas dataFrame으로 변환 한다. ?
        # to-do 2. 파라메터로 받은 시작 종료일로 주가 표시할 기간 만큼 dataFrame을 slicing 한다.
        # to-do 3. 파라메터로 받은 종목코드로 종목명을 가져와 챠트 제목에 달아준다.
        df = self.getDailyPrice(itemcode)
        df = df.iloc[0:30] #to-do 2 참고할 것
        df = df.rename(columns={'날짜':'Date', '시가':'Open', '고가':'High', '저가':'Low', '종가':'Close', '거래량':'Volume'})
        df = df.sort_values(by='Date')
        df.index = pd.to_datetime(df.Date)
        df = df['Open', 'High', 'Low', 'Close', 'Volume']

        kwargs = dict(title='{} candle chart'.format(itemcode), type='candle', mav=(2, 4, 6), value=True, ylabel='ohlc candles')
        mc = mpf.make_marketcolors(up='r', down='b', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)
        mpf.plot(df, **kwargs, style=s)