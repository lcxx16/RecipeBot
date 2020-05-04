"""handler.py
    * callbackから受け取ったデータを保持する
    * observerにデータを受け取ったことを通知する
"""

from abc import ABCMeta, abstractmethod
from setting import *
import datetime
import json
from linebot import (
    LineBotApi
)

line_bot_api = LineBotApi(BOT.YOUR_CHANNEL_ACCESS_TOKEN)


class AbstractHandler(metaclass=ABCMeta):
    """AbstractObserver
        * handlerの抽象クラス

    Attributes:
        None
    """

    def __init__(self):
        self.__observers = []

    def add_observer(self, observer):
        """add_observer
            * observerを追加する

        Args:
            observer (obj): observer
        """
        self.__observers.append(observer)

    def notify_observer(self):
        """notify_observer
            * observerにデータを通知する
        """
        for obs in self.__observers:
            try:
                obs.update(self)
            except Exception as e:
                print(e.args)
                self.error_setter()

    @abstractmethod
    def execute(self) -> None:
        """execute
            * handlerのmain処理を記述
        """
        pass

    @abstractmethod
    def error_setter(self) -> None:
        """error_setter
            * Error発生時にTrueにする
        """
        pass


class MessageHandler(AbstractHandler):
    """MessageHandler
        * handlerの抽象クラス

    Attributes:
        None
    """
    def __init__(self, event):
        super(MessageHandler, self).__init__()
        self.error = False
        self.event = event
        self.type = event.type
        self.message_type = event.message.type
        self.message = ''
        self.user_id = event.source.user_id
        self.status = Status()
        self.reset_status_col = 0

    def execute(self):
        # TEXTメッセージ
        if self.message_type == 'text':
            self.message = self.event.message.text
            self.reset_status_col = self.check_push_menu(self.message)

        # SELECT * FROM status WHERE user_id = ? ;
        status = session.query(Status). \
            filter(Status.user_id == self.user_id). \
            first()
        self.status = status

        self.notify_observer()

    def error_setter(self):
        self.error = True

    @staticmethod
    def check_push_menu(message):
        """check_push_menu
            * 選択されたメニューボタンとstatusテーブルとの対応を返す
        Args:
            message (str): 入力されたメッセージ
        Returns:
            StatusColumn(int): statusテーブルのカラム位置
        """
        if message == MenuType.REGISTER:
            return StatusColumn.REGISTER
        elif message == MenuType.LIST:
            return StatusColumn.LIST
        elif message == MenuType.RECIPE:
            return StatusColumn.RECIPE
        else:
            return StatusColumn.NONE


class PostbackHandler(AbstractHandler):
    """PostbackHandler
        * handlerの抽象クラス

    Attributes:
        None
    """
    
    def __init__(self, event):
        super(PostbackHandler, self).__init__()
        self.error = False
        self.event = event
        self.type = event.type
        self.sequence = ''
        self.command = ''
        self.message = ''
        self.user_id = event.source.user_id
        self.status = Status()

    def execute(self):
        postback_data_str = self.event.postback.data
        postback_data_json = json.loads(postback_data_str)

        self.sequence = postback_data_json['sequence']
        self.command = postback_data_json['command']
        self.data_json = postback_data_json

        # SELECT * FROM status WHERE user_id = ? ;
        status = session.query(Status). \
            filter(Status.user_id == self.user_id). \
            first()
        self.status = status

        self.notify_observer()

    def error_setter(self):
        self.error = True


class FollowHandler(AbstractHandler):
    """FollowHandler
        * handlerの抽象クラス

    Attributes:
        None
    """

    def __init__(self, event):
        super(FollowHandler, self).__init__()
        self.error = False
        self.event = event
        self.type = event.type
        self.user = User()
        self.user_id = event.source.user_id
        self.profile = ''
        self.insert_flag = True

    def execute(self):
        # SELECT * FROM user WHERE user_id = ? ;
        self.user = session.query(User). \
            filter(User.user_id == self.user_id). \
            first()

        if self.type == 'follow':
            self.profile = line_bot_api.get_profile(self.user_id)
       
        self.notify_observer()

    def error_setter(self):
        self.error = True