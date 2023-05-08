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