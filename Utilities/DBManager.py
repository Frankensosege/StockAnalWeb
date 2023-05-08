import psycopg2
from Utilities.comUtilities import commonUtilities as cu
from sqlalchemy import create_engine, text

class DBman:
    def __init__(self):
        from Utilities.UsrLogger import stockLogger as sl
        self.logger = sl(__name__).get_logger()
        self.prop = cu('./config.ini')
        self.host = self.prop.get_property('DB', 'hostname')
        self.dbname = self.prop.get_property('DB', 'dbname')
        self.user = self.prop.get_property('DB', 'username')
        self.password = self.prop.get_property('DB', 'password')
        self.port = self.prop.get_property('DB', 'port')

    def get_connection(self):
        try:
            self.conn = psycopg2.connect(
                                         host=self.host,
                                         dbname=self.dbname,
                                         user=self.user,
                                         password=self.password,
                                         port=self.port
                                         )
        except Exception as e:
            self.logger.error('get_connection', e)
            return None
        return self.conn

    def get_alchmy_con(self, mode):

        engine = create_engine(
            'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(self.user, self.password, self.host, self.port, self.dbname),
            isolation_level=mode
        )
        return engine

    def get_alchemy_query(self, query):
        return text(query)

    def excuteSQL(self, sqlStr):
        try:
            cur = self.conn.cursor()
            cur.execute(sqlStr)
        except Exception as e:
            self.logger.error('excuteSQL', e)
            return None

        return 0