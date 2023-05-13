import json

def get_menu_list(auth):
    menu_list = {}

    if auth=='A':
        menu_list = {'menu_items':
            [
                {"name": "사용자 관리",
                 "url": "",
                 "submenu": []
                 },
                {"name": "분석툴관리",
                 "url": "",
                 "submenu": []
                 },
                {"name": "주가관리",
                 "url": "",
                 "submenu": []
                 },
                {"name": "모델관리",
                 "url": "",
                 "submenu": []
                 },
                {"name": "재무제표",
                 "url": "",
                 "submenu": []
                 }
            ]
        }
    elif auth == 'U':
        menu_list = {'menu_items':
            [
                {"name": "포트폴리오",
                 "url": "",
                 "submenu": [
                     {"name": "포트폴리오구성",
                      "url": "{% url 'investar:create_portpolio' %}"},
                     {"name": "주가동향",
                      "url": "{% url 'investar:daily_price' %}"}
                 ],
                 },

                {"name": "분석툴",
                 "url": "",
                 "submenu": [
                     {"name": "분석툴 선택",
                      "url": "{% url 'investar:create_portpolio' %}"},
                     {"name": "분석조회",
                      "url": "{% url 'investar:daily_price' %}"}
                 ]
                 }
            ]
        }
    else:
        menu_list = {}

    return json.dumps(menu_list)

class commonUtilities:
    def __init__(self, propFile):
        self.propFile = propFile

    def get_property(self, propSection, propName):
        #property 파일에서 property 읽어오기
        import configparser as parser

        properties = parser.ConfigParser()
        properties.read(self.propFile, "utf-8")
        propertiesSection = properties[propSection]

        return propertiesSection[propName]