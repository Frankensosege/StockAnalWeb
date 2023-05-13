# import psycopg2 dbl
import MySQLdb as dbl
from Utilities.comUtilities import commonUtilities as cu
from sqlalchemy import create_engine, text
import config.settings as conf

class DBman:
    def __init__(self):
        from Utilities.UsrLogger import stockLogger as sl
        dbconf = conf.DATABASES['default']
        self.logger = sl(__name__).get_logger()
        self.prop = cu('./config.ini')
        self.host = dbconf['HOST']   # self.prop.get_property('DB', 'hostname')
        self.dbname = dbconf['NAME']   # self.prop.get_property('DB', 'dbname')
        self.user = dbconf['USER']   # self.prop.get_property('DB', 'username')
        self.password = dbconf['PASSWORD']   # self.prop.get_property('DB', 'password')
        self.port = dbconf['PORT']   # self.prop.get_property('DB', 'port')

    def get_connection(self):
        try:
            self.conn = dbl.connect(
                                         host=self.host,
                                         # dbname=self.dbname,  --> postgreSQL
                                         db=self.dbname, # MySQL
                                         user=self.user,
                                         password=self.password,
                                         # port=self.port   --> postgreSQL
                                         port=int(self.port) # MySQL
                                         )
        except Exception as e:
            self.logger.error('get_connection', e)
            return None
        return self.conn

    def get_alchmy_con(self, mode):

        engine = create_engine(
            # 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(self.user, self.password, self.host, self.port, self.dbname),  --> postgreSQL
            'mysql+mysqldb://{}:{}@{}:{}/{}'.format(self.user, self.password, self.host, self.port, self.dbname), # MySQL
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