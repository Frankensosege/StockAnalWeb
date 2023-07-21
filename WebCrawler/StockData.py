import pandas as pd
from bs4 import BeautifulSoup
import requests
from Utilities.comUtilities import get_property
# import mplfinance as mpf
from Utilities.UsrLogger import stockLogger as sl
import dart_fss as dart
import time
from datetime import datetime

# class anlDataMng:

def getItemList():
    #한국거래소 기업공시 체널에서 종목 목록 가져오기
    try:
        url = '{}{}{}'.format(get_property('URLs', 'kind'),
                                get_property('URLs', 'kindItemPage'),
                                '/corpList.do?method=download&searchType=13')
        print(url)
        df = pd.read_html(url)[0]
        df = df[['종목코드', '회사명']]
        df = df.rename(columns={'종목코드':'code', '회사명':'company'})
        df.code = df.code.map('{:06d}'.format)
    except Exception as e:
        sl(__name__).get_logger().error("getItemList : " + str(e))
        return None

    return df

def __getLastPageNaver(url):
    #네이버 금융에서 종목별 과거 주가가져오기

    lp_html = requests.get(url, headers={'User-agent':'Mozilla/5.0'}).text
    bs = BeautifulSoup(lp_html, 'lxml')
    pgrr = bs.find('td', class_=get_property('ETC', 'naverLpageClass'))
    if pgrr == None:
        return None
    s = str(pgrr.a['href']).split('=')
    # print('-----------------------------------')
    # print(s, s[-1])

    return s[-1]

def getDailyPriceNaver(itemCode, company, pages_to_fetch=0, start_date=None):
    # # 기관 외국인 전일비 거래증감량
    # df_frgv_trade = for_gov_trading(itemCode, start_date=start_date)
    # print(df_frgv_trade)
    #
    # return None

    #Naver 종목별 시세 페이지
    try:
        url = get_property('URLs', 'naverFinance')
        url = '{}{}?code={}'.format(url, get_property('URLs', 'naverItmePrice'), itemCode)
        # Naver 종목별 시세 마지막 페이지 가져오기
        urlpage = '{}&page=1'.format(url)
        lastpg = __getLastPageNaver(urlpage)
        if lastpg == None:
            return None
        df = pd.DataFrame()

        if start_date is not None:
            str_dt = datetime.strptime(start_date, '%Y-%m-%d')

        if pages_to_fetch == 0:
            pages = int(lastpg)
        else:
            pages = min(int(lastpg), int(pages_to_fetch))

        for page in range(1, pages + 1):
            prcUrl = '{}&page={}'.format(url, page)

            html = requests.get(prcUrl, headers={'User-agent': 'Mozilla/5.0'}).text

            dayily_price = pd.read_html(html, header=0)[0]
            dayily_price.dropna(inplace=True)

            if start_date is not None:
                dayily_price = dayily_price[dayily_price['날짜'].apply(lambda x: datetime.strptime(x, '%Y.%m.%d') >= str_dt)]

                if len(dayily_price) < 10 or len(dayily_price) == 0:
                    if len(dayily_price) > 0:
                        df = df.append(dayily_price)
                    break

            if page % 10 == 0:
                time.sleep(20)
            df = df.append(dayily_price)
            print("getDailyPriceNaver : Download {}:{} - Page {:04d} / {:04d}".format(itemCode, company, page, pages))
            # self.logger.info("getDailyPriceNaver : Download {}:{} - Page {:04d} / {:04d}".format(itemCode, company, page, pages))
        # 기관 외국인 전일비 거래증감량
        lst_dt = df.iloc[-1, 0].replace('.', '-')
        df_frgv_trade = for_gov_trading(itemCode, start_date=lst_dt)

        df = pd.merge(left=df, right=df_frgv_trade, how="outer", on='날짜')

        df = df.rename(columns={'날짜':'date', '종가':'close', '전일비':'differ', '시가':'open', '고가':'high', '저가':'low', '거래량':'volume', '기관':'gov_trade', '외국인':'for_trade'})
        df['date'] = df['date'].replace('.', '-')

        df = df.dropna()
        df[['close', 'differ', 'open', 'high', 'low', 'volume', 'gov_trade', 'for_trade']] = df[['close', 'differ', 'open', 'high', 'low', 'volume', 'gov_trade', 'for_trade']].astype(int)
        df = df[['date', 'open', 'high', 'low', 'close', 'differ', 'volume', 'gov_trade', 'for_trade']]
    except Exception as e:
        print(e)
        sl(__name__).get_logger().error("getDailyPriceNaver : " + str(e))
        return None

    return df

# def drawCandleChart(self, sdate, ldate, itemcode):
#     #읽어온 데이터를 캔들 챠트로 출력한다.
#     # to-do 1. Item 코드로 DB에서 데이터 읽어어와 pandas dataFrame으로 변환 한다. ?
#     # to-do 2. 파라메터로 받은 시작 종료일로 주가 표시할 기간 만큼 dataFrame을 slicing 한다.
#     # to-do 3. 파라메터로 받은 종목코드로 종목명을 가져와 챠트 제목에 달아준다.
#     df = self.getDailyPrice(itemcode)
#     df = df.iloc[0:30] #to-do 2 참고할 것
#     df = df.rename(columns={'날짜':'Date', '시가':'Open', '고가':'High', '저가':'Low', '종가':'Close', '거래량':'Volume'})
#     df = df.sort_values(by='Date')
#     df.index = pd.to_datetime(df.Date)
#     df = df['Open', 'High', 'Low', 'Close', 'Volume']
#
#     kwargs = dict(title='{} candle chart'.format(itemcode), type='candle', mav=(2, 4, 6), value=True, ylabel='ohlc candles')
#     mc = mpf.make_marketcolors(up='r', down='b', inherit=True)
#     s = mpf.make_mpf_style(marketcolors=mc)
#     mpf.plot(df, **kwargs, style=s)

def get_dart_fss(item_code, bgn_de, report, report_tp=['quarter']):
    # Open DART API KEY 설정
    api_key = get_property('DART', 'api_key')
    dart.set_api_key(api_key=api_key)

    try:
        # DART 에 공시된 회사 리스트 불러오기
        corp_list = dart.get_corp_list()

        dart_comp = corp_list.find_by_stock_code(item_code)
        fs = dart_comp.extract_fs(bgn_de=bgn_de, report_tp=report_tp)
    except Exception as e:
        print(e)
        # sl(__name__).get_logger().error("getDailyPriceNaver : " + str(e))
        return None

    if report=='all':
        report = ['bs', 'is', 'cis', 'cf']  ## 4개의 보고서
    else:
        report = [report]

    data_dict = {}  ## 데이터 프레임 만들기전에 dict형태로 저장

    for i in report:
        report_ = i
        df = fs.show(report_, show_class=False, show_concept=False)  ## 각각의 제무재표를 가져옴

        if df is None:  ## df가없으면 다음으로 넘어간다
            continue
        else:
            new_index = df.columns.get_level_values(0)[2::].to_list()  ## 멀티 인덱스 문제 해결을 위해 멀티인덱스중 필요한 부분 가져옴
            df.columns = range(df.shape[1])  ##멀티 인덱스 삭제 및 해결부분
            df.index.names = [None] * len(df.index.names)  # 멀티 인덱스 삭제 및 해결부분
            columns = ['ko', 'en'] + new_index  ## 한글명, 영어명 +인덱스 추출부분으로 데이터프레임 재생산
            df.columns = columns
            data_dict['data_' + i] = df  ## 전치해서 딕셔너리에 저장

    return data_dict

    # try:
    #     data_bs = data_dict['data_bs']
    #     data_is = data_dict['data_is']
    #     data_cis = data_dict['data_cis']
    #     data_cf = data_dict['data_cf']
    # except KeyError as e:  ## 오류가 나는 부분은 어디인지 전송
    #     print("Error:", e, "is missing in data_dict.")

def for_gov_trading(itemCode, start_date=None):
    url = get_property('URLs', 'naverFinance')
    url = '{}{}?code={}'.format(url, get_property('URLs', 'naverFrGvTrade'), itemCode)
    page = 0

    col_list = []
    eod=False
    while True:
        page += 1
        tradeUrl = '{}&page={}'.format(url, page)
        print('기관, 외국인 보유변화 page: ', page)

        response = requests.get(tradeUrl, headers={'User-agent': 'Mozilla/5.0'})
        if response.status_code!=200:
            raise Exception("1. 외국인 기관 거래량을 가져오지 못했습니다.")
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        temp = soup.find_all('table', class_='type2')
        if (len(temp)<1):
            print('더이상 자료가 없습니다.')
            break

        if start_date is not None:
            str_dt = datetime.strptime(start_date, '%Y-%m-%d')
        rows = temp[1].find_all('tr')

        for idx in range(3, len(rows)):
            cols = rows[idx].find_all('td')

            if len(cols) >= 8:
                try:
                    trade_date = datetime.strptime(cols[0].get_text().strip(), '%Y.%m.%d')
                except Exception as e:
                    print(str(e))
                    eod = True
                    break

                if str_dt > trade_date:
                    eod = True
                    break

                col_list.append([cols[0].get_text().strip(), cols[5].get_text().strip(), cols[6].get_text().strip()])
        if eod:
            break
    df = pd.DataFrame(col_list, columns=['날짜', '기관', '외국인'])
    df['기관'] = df['기관'].str.replace(',', '')
    df['외국인'] = df['외국인'].str.replace(',', '')
    # df['기관'] = df['기관'].astype('int64')
    # df['외국인'] = df['외국인'].astype('int64')

    return df

