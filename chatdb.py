#pip install SQLAlchemy
#pip install mysql-connector-python

import time
from datetime import datetime
import loguru

import sqlalchemy
import sqlalchemy.ext.automap
import sqlalchemy.orm
import sqlalchemy.schema

class ChatDB(object):

    #資料表(常數)
    __bot_options__ = 'bot_options'
    __bot_chatmeta__ = 'bot_chatmeta'
    __bot_chats__ = 'bot_chats'
    __bot_usermeta__ = 'bot_usermeta'
    __bot_users__ = 'bot_users'

    def __init__(self, config):
        self.host = config['Host']
        self.port = int(config['Port'])
        self.username = config['User']
        self.password = config['Password']
        self.database = config['Database']
        self.chartset = config['Charset']
        self.automap = None
        self.session = None

    # 建立連線引擎
    def connect(self):
        connect_string = connect_string = 'mysql+mysqlconnector://{}:{}@{}:{}/{}?charset={}'.format(self.username, self.password, self.host, self.port, self.database, self.chartset)
        connect_args = {'connect_timeout': 10}
        engine = sqlalchemy.create_engine(connect_string, connect_args=connect_args, echo=False)
        # 取得資料庫元資料
        self.metadata = sqlalchemy.schema.MetaData(engine)
        # 產生自動對應參照
        self.automap = sqlalchemy.ext.automap.automap_base()
        self.automap.prepare(engine, reflect=True)
        # 準備 ORM 連線
        self.session = sqlalchemy.orm.Session(engine)

        loguru.logger.add(
            f'{datetime.today().strftime("%Y%m%d")}.log',
            encoding="utf-8",
            rotation='1 day',
            retention='7 days',
            level='DEBUG'
        )

    # 關閉連線引擎
    def close(self):
        self.session.close()

    # 建立使用者基本資料
    def create_user(self, data):
        created = int(time.mktime(datetime.now().timetuple()))

        sqlalchemy.Table(self.__bot_users__, self.metadata, autoload=True)
        User = self.automap.classes[self.__bot_users__]

        user = User()
        user.telegram_user_id = data['user_id']
        user.telegram_chat_id = data['chat_id']
        user.user_nicename = data['nicename']
        user.user_email = ''
        user.user_phone = ''
        user.user_created = created
        user.user_status = 1
        user.display_name = data['display_name']

        self.session.add(user)
        self.session.flush()

        try:
            self.session.commit()
            loguru.logger.info('新增使用者成功')
            return user.ID
        except Exception as e:
            loguru.logger.error('新增使用者失敗')
            loguru.logger.error(e)
            self.session.rollback()
            return None

    # 查詢使用者基本資料
    def find_user(self, data):
        sqlalchemy.Table(self.__bot_users__, self.metadata, autoload=True)
        User = self.automap.classes[self.__bot_users__]

        user = self.session.query(User).filter(
            User.telegram_user_id == data['user_id'],
            User.telegram_chat_id == data['chat_id']
        ).first()
        
        if user:
            return user.ID
        else:
            return None

    def create_chat(self, data):
        created = int(time.mktime(datetime.now().timetuple()))
        
        sqlalchemy.Table(self.__bot_chats__, self.metadata, autoload=True)
        Chat = self.automap.classes[self.__bot_chats__]

        chat = Chat()
        chat.chat_user = data['chat_user']
        chat.chat_created = created
        chat.chat_ask = data['chat_ask']
        chat.bot_response = data['bot_response']
        chat.bot_response_type = data['bot_response_type']
        chat.chat_parent = data['chat_parent']
        chat.chat_intent = data['chat_intent']
        chat.chat_action = data['chat_action']
        chat.chat_entity = data['chat_entity']
        chat.chat_context = data['chat_context']

        self.session.add(chat)
        self.session.flush()

        try:
            self.session.commit()
            loguru.logger.info('新增對話記錄成功')
            return chat.ID
        except Exception as e:
            loguru.logger.error('新增對話記錄失敗')
            loguru.logger.error(e)
            self.session.rollback()
            return None



    
