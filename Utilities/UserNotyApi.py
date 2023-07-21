import requests
import json
from Utilities.comUtilities import commonUtilities
from Utilities.UsrLogger import stockLogger as sl

## KAKAO API를 사용한 내게 메세지 보내기
## 친구 목록 가져오기 및 친구에게 보내기 추가해야 한다.
## 필요한 경우 다른 API를 class를 구현 한다(email, 문자메세지, mobile app 관련 rest API 등등...)
class KatalkApi:
    ### 인증 토큰을 받아 json 형태로 저장
    def __init__(self):
        self.logger = sl(__name__).get_logger()
        self.cu = commonUtilities('./config.ini')

    def getJson(self):
        token_path = self.cu.get_property('DATA', 'jasonpath')
        data = {
            'grant_type':'authorization_code',
            'client_id': self.cu.get_property('Kakao', 'client_id'),
            'redirect_uri': self.cu.get_property('Kakao', 'redirect_uri'),
            'code': self.cu.get_property('Kakao', 'code'),
            }

        response = requests.post(self.cu.get_property('Kakao', 'url'), data=data)
        tokens = response.json()

        #발행된 토큰 저장
        try:
            with open(token_path + "kakaotoken.json","w") as kakao:
                json.dump(tokens, kakao)
        except Exception as e:
            return e
        return None


    ## 저장되어 있는 토큰 정보를 가지고 메시지를 보내기
    def sendMessage(self, message):
        # 발행한 토큰 불러오기
        token_path = self.cu.get_property('DATA', 'jasonpath')
        with open(token_path + "kakaotoken.json", "r") as kakao:
            tokens = json.load(kakao)

        url = self.cu.get_property('Kakao', 'send_url')

        headers = {
            "Authorization": "Bearer " + tokens["access_token"]
        }

        data = {
            'object_type': 'text',
            'text': message,
            'link': {
                'web_url': 'https://developers.kakao.com',
                'mobile_web_url': 'https://developers.kakao.com'
            }
        }

        try:
            data = {'template_object': json.dumps(data)}
            response = requests.post(url, headers=headers, data=data)
        except Exception as e:
            return e
        return response.status_code