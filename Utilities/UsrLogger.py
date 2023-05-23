import logging
from Utilities.comUtilities import get_property
import logging.handlers
import os

class stockLogger():
    def __init__(self, module_name, file_name=None, log_type=None):
        self.modul_name = module_name
        logLevel = get_property("LOG", "loglevel")
        logpath = get_property("LOG", "fileLoc")

        try:
            if not os.path.exists(logpath):
                os.makedirs(logpath)
        except Exception as e:
            print(e)

        if log_type is None:
            logfile = get_property("LOG", "LogName")

            self.logger = logging.getLogger(self.modul_name + ' : ')
            self.logger.setLevel(self.__get_level(logLevel))
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s")
            timedfilehandler = logging.handlers.TimedRotatingFileHandler(filename=logpath + logfile, when='midnight', interval=1,
                                                                         encoding='utf-8')
            timedfilehandler.setFormatter(formatter)
            timedfilehandler.suffix = "%Y%m%d"

            console = logging.StreamHandler()
            console.setLevel(logging.INFO)

            #7 logger에 handler 추가합니다.
            self.logger.addHandler(timedfilehandler)
            self.logger.addHandler(console)
        else:
            log_path = os.path.join(get_property('LOG', 'fileLoc'), f'{file_name}.log')
            if os.path.exists(log_path):
                os.remove(log_path)
            logging.basicConfig(format='%(message)s')
            self.logger = logging.getLogger(get_property('LOG', 'ML_LOGGER_NAME'))
            self.logger.setLevel(logging.DEBUG)
            self.logger.propagate = False
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            file_handler = logging.FileHandler(filename=log_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(stream_handler)
            self.logger.addHandler(file_handler)

    def get_logger(self):

        #8 설정된 log setting을 반환합니다.
        return self.logger

    # def __init__(self, module):
    #     super().__init__(self)
    #     conf = cu("./config.ini")
    #     logLevel = conf.get_property( "LOG", "loglevel")
    #     self.module = module
    #     self.file_handler = logging.FileHandler(conf.get_property("LOG", "fileLoc"), "w", encoding="UTF-8")
    #     formatter = logging.Formatter("[%(asctime)s] : %(message)s")
    #     stream_handler = logging.StreamHandler()
    #     stream_handler.setFormatter(formatter)
    #     self.addHandler(stream_handler)
    #     self.file_handler.setFormatter(formatter)
    #     self.setLevel(self.__get_level(logLevel))
    #
    # def get_logger(self, name):
    #     pass

    def __get_level(self, confLevel):
        return {'DEBUG':logging.DEBUG, 'INFO':logging.INFO, 'WARNING':logging.WARNING, 'ERROR':logging.ERROR, 'WARNING':logging.WARNING}[confLevel]