import json

def get_menu_list(userid):
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
                     {"name": "포트폴리오구성",
                      "url": "{% url 'investar:create_portpolio' %}"},
                     {"name": "주가동향",
                      "url": "{% url 'investar:daily_price' %}"}
                 ]
             }
        ]
    }

    return json.dumps(menu_list)

class commonUtilities:
    def __init__(self, propFile):
        self.propFile = propFile

    def get_property(self, propSection, propName):
        #property 파일에서 property 읽어오기
        import configparser as parser

        properties = parser.ConfigParser()
        properties.read(self.propFile)
        propertiesSection = properties[propSection]

        return propertiesSection[propName]