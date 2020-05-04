"""observer.py
    * handler(subject)から受け取ったデータを処理するobserverの処理を記述
    * AbstractObserverを継承したクラスの各処理が実行される。
"""

from abc import ABCMeta, abstractmethod
from setting import *
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, FollowEvent, UnfollowEvent, PostbackEvent
)

from linebot import (
    LineBotApi
)
import pykakasi
import datetime
import copy
import json

line_bot_api = LineBotApi(BOT.YOUR_CHANNEL_ACCESS_TOKEN)


class AbstractObserver(metaclass=ABCMeta):
    """AbstractObserver
        * observerの抽象クラス

    Attributes:
        None
    """

    @abstractmethod
    def update(self, handler) -> None:
        """update
            * observerのmain処理を記述

        Args:
            handler (obj): handlerのインスタンス
        """
        pass

    def check_invalid_request(self, handler):
        """check_invalid_request
            * メッセージイベントが正しいフォーマットかチェックする

        Args:
            handler (:obj:MessageHandler): MessageHandlerのインスタンス

        Returns:
           True or False: True なら不正なフォーマット, False なら正しいフォーマット)
        """

        # *** 明示的に拒否するメッセージ ***
        # TEXT以外のメッセージ 
        if handler.message_type != 'text':
            return True

        # 15文字以上のTEXT **
        if len(handler.message) > 15:
            return True

        # *** 明示的に許諾するメッセージ ***
        # メニューボタン押下時のイベント
        if handler.reset_status_col != 0:
            return False
            
        # 商品登録時の商品名入力
        if handler.status.register_status == RegisterStatus.WAIT_PRODUCT:
                return False

        return True
    
    def check_invalid_postback(self, handler):
        """check_invalid_postback
            * ポストバックイベントが正しいフォーマットかチェックする

        Args:
            handler (:obj:PostbackHandler): PostbackHandlerのインスタンス

        Returns:
           True or False: True なら不正なフォーマット, False なら正しいフォーマット
        """

        # 登録処理 - Datepicker入力待ち
        if handler.status.register_status == RegisterStatus.WAIT_DATE:
            if handler.sequence == PostbackSEQ.REGISTER_EXPIRE: 
                return False
        
        # 一覧処理 - 商品選択待ち
        if handler.status.list_status == ListStatus.WAIT_PRODUCT:
            if handler.sequence == PostbackSEQ.LIST_PRODUCT: 
                return False
        
        # 一覧処理 - アクション選択待ち
        if handler.status.list_status == ListStatus.WAIT_SELECT:
            if handler.sequence == PostbackSEQ.LIST_SELECT: 
                return False

        # 一覧処理 - Datepicker入力待ち
        if handler.status.list_status == ListStatus.WAIT_DATE:
            if handler.sequence == PostbackSEQ.LIST_EXPIRE: 
                return False
        
        # レシピ処理 - 商品選択待ち
        if handler.status.recipe_status == RecipeStatus.WAIT_PRODUCT:
            if handler.sequence == PostbackSEQ.RECIPE_PRODUCT: 
                return False
        
        return True


    def get_datetime(self):
        """get_datetime
            * yyyymmdd の現在日付をstr型で返す

        Returns:
           str: yyyymdd の現在日付
        """
        date = datetime.datetime.now()
        return str(date.year * 10000 + date.month * 100 + date.day)
    
    def convert_date(self, date):
        """get_datetime
            * yyyy-mm-dd の日付を yyyymmdd のint型で返す

        Args:
            date(str): yyyy-mm-dd の 日付データ

        Returns:
           int: yyyymdd の日付
        """
        split_date = date.split("-")
        return int(split_date[0]) * 10000 + int(split_date[1]) * 100 + int(split_date[2])


class UserObserver(AbstractObserver):
    """UserObserver
        * userテーブルの更新をするobserverクラス

    Attributes:
        None
    """
    
    def update(self, handler):
        # エラー発生時
        if handler.error:
            return

        # INSERT
        if handler.user is None:
            user = User()
            user.user_id = handler.user_id
            user.user_name = handler.profile.display_name
            user.user_photo = handler.profile.picture_url
            user.register_date = super().get_datetime()

            # INSERT INTO user... ;
            session.add(user)
            session.commit()
            return
        
        # followイベント
        if handler.type == 'follow':
            # UPDATE user SET status = '1' ;
            handler.user.status = '1'
            session.commit()

        # unfollowイベント
        if handler.type == 'unfollow':
            # UPDATE user SET status = '0' ;
            handler.user.delete_date = super().get_datetime()
            handler.user.status = '0'
            session.commit()


class StatusObserver(AbstractObserver):
    """StatusObserver
        * statusテーブルの更新をするobserverクラス

    Attributes:
        None
    """
    def update(self, handler):
        # エラー発生時
        if handler.error:
            return

        # Followイベント
        if handler.type == 'follow':
            # INSERT INTO status ... ;
            status = Status()
            status.user_id = handler.user_id
            session.add(status)
            session.commit()
            return

        # Unfollowイベント
        if handler.type == 'unfollow':
            # DELETE FROM status
            session.query(Status). \
                filter(Status.user_id == handler.user_id). \
                delete()
            session.commit()
            return

        # Messageイベント
        if handler.type == 'message':
            # フォーマットチェック
            if super().check_invalid_request(handler):
                return
            
            # SELECT * FROM status where user_id = ? ;
            status = session.query(Status). \
                filter(Status.user_id == handler.user_id). \
                first()
            
            # メニューボタン選択時
            if handler.reset_status_col != 0:
                status = self.reset_status(status, handler.reset_status_col)
                session.commit()
                return

            # 登録処理 - 商品名入力時
            if status.register_status == RegisterStatus.WAIT_PRODUCT:
                status.register_status = RegisterStatus.WAIT_DATE
                session.commit()
                return
        
        # Postbackイベント
        if handler.type == 'postback':
            # フォーマットチェック
            if super().check_invalid_postback(handler):
                return

            # SELECT * FROM status where user_id = ? ;
            status = session.query(Status). \
                filter(Status.user_id == handler.user_id). \
                first()

            # 登録処理 - Datepicker入力時 (WAIT_DATE → INIT)
            if handler.sequence == PostbackSEQ.REGISTER_EXPIRE:
                status.register_status = RegisterStatus.INIT
                session.commit()
                return

            # 一覧処理 - 商品選択時 (WAIT_PRODUCT → WAIT_SELECT)
            if status.list_status == ListStatus.WAIT_PRODUCT:
                if handler.command == Command.SELECT_PRODUCT:
                    status.list_status = ListStatus.WAIT_SELECT
                    session.commit()
                    return
            
            # 一覧処理 - アクション選択時
            if status.list_status == ListStatus.WAIT_SELECT:
                # 日付変更選択時 (WAIT_SELECT → WAIT_DATE)
                if handler.command == Command.CHANGE_DATE:
                    status.list_status = ListStatus.WAIT_DATE
                    session.commit()
                    return
                
                # 商品削除選択時 (WAIT_SELECT → INIT)
                if handler.command == Command.DELETE:
                    status.list_status = ListStatus.INIT
                    session.commit()
                    return
            
            # 一覧処理 - Datepicker入力時 (WAIT_DATE → INIT)
            if status.list_status == ListStatus.WAIT_DATE:
                status.list_status = ListStatus.INIT
                session.commit()
                return
            
            # レシピ処理 - 検索時 
            if status.recipe_status == RecipeStatus.WAIT_PRODUCT:
                # 検索選択時 (WAIT_PRODUCT → INIT)
                if handler.command == Command.SEARCH:
                    status.recipe_status = RecipeStatus.INIT
                    session.commit()
                    return

            
    @staticmethod
    def reset_status(status, reset_status_col):
        """reset_status
            * メニューボタン選択時にステータスを初期化する

        Args:
            status(:obj:Status): Statusのインスタンス
            reset_status_col(int): 選択されたメニューとstatusテーブルのカラムの対応

        Returns:
           status(obj): 初期化状態のstatusインスタンス
        """

        # メニューボタン未選択
        if reset_status_col == 0:
            return status
        
        # ステータス初期化
        status.register_status = RegisterStatus.INIT
        status.list_status = ListStatus.INIT
        status.recipe_status = RecipeStatus.INIT

        # メニューボタンで選択されたカラムのみステータス変更
        if reset_status_col == 1:
            status.register_status = RegisterStatus.WAIT_PRODUCT
        elif reset_status_col == 2:
            status.list_status = ListStatus.WAIT_PRODUCT
        elif reset_status_col == 3:
            status.recipe_status = RecipeStatus.WAIT_PRODUCT
        
        return status



class ProductObserver(AbstractObserver):
    """ProductObserver
        * productテーブルの更新をするobserverクラス

    Attributes:
        None
    """

    def update(self, handler):
        # エラー発生時
        if handler.error:
            return

        # Postbackイベント
        if handler.type == 'postback':
            # フォーマットチェック
            if super().check_invalid_postback(handler):
                return

            # INSERT (登録処理 - Datepicker入力時)
            if self.check_action(handler) == 'INSERT':
                product_name = handler.data_json['product_name']

                # 形態素解析
                kakasi = pykakasi.kakasi()
                kakasi.setMode('J', 'K') # H(Kanji) to K(Katakana)
                kakasi.setMode('K', 'K') # K(Katakana) to K(Katakana)
                kakasi.setMode('H', 'K') # J(Hiragana) to aK(Katakana)

                conv = kakasi.getConverter()
                product_kana = conv.do(product_name)

                product = Product()
                product.product_name = product_name
                product.product_kana = product_kana
                product.user_id = handler.user_id
                product.register_date = super().get_datetime()
                product.expire_date = super().convert_date(handler.event.postback.params['date'])
                session.add(product)
                session.commit()
                return
            
            # UPDATE (一覧処理 - Datepicker入力時)
            if self.check_action(handler) == 'UPDATE':
                # SELECT * FROM product WHERE product_id = ? ;
                product = session.query(Product). \
                    filter(Product.product_id == handler.data_json['product_id']). \
                    first()

                product.expire_date = super().convert_date(handler.event.postback.params['date'])
                session.commit()
                return
            
            # DELETE (一覧処理 - 商品削除入力時)
            if self.check_action(handler) == 'DELETE':
                product = session.query(Product). \
                    filter(Product.product_id == handler.data_json['product_id']). \
                    delete()
                session.commit()
                return


    @staticmethod
    def check_action(handler):
        """check_action
            * Postbackイベントを受けた状況から操作すべきSQL区分を返す

        Args:
            handler(obj): handlerのインスタンス

        Returns:
           'INSERT' or 'UPDATE' or 'DELETE' or 'NONE'(str): SQL実行の区分
        """

        # 登録処理で発行されたDatepicker
        if handler.sequence == PostbackSEQ.REGISTER_EXPIRE:
            # Datepicker選択時
            if handler.command == Command.DATEPICKER:
                return 'INSERT'

        # 一覧処理で発行されたアクション選択メッセージ
        if handler.sequence == PostbackSEQ.LIST_SELECT:
            # 商品削除選択時
            if handler.command == Command.DELETE:
                return 'DELETE'

        # 一覧処理で発行されたDatepicker
        if handler.sequence == PostbackSEQ.LIST_EXPIRE:
            # Datepicker選択時
            if handler.command == Command.DATEPICKER:
                return 'UPDATE'
            
        return 'NONE'
        

class MessageObserver(AbstractObserver):
    """MessageObserver
        * 送信するメッセージを作成するobserverクラス

    Attributes:
        None
    """

    def update(self, handler):
        # エラー発生時
        if handler.error:
            self.reply_text_message(handler, Message.ERROR)
            return

        # Followイベント
        if handler.type == 'follow':
            self.reply_text_message(handler, Message.USER_REGISTER)
            return

        # Messageイベント
        if handler.type == 'message':
            # フォーマットチェック
            if super().check_invalid_request(handler):
                self.reply_text_message(handler, Message.INVALID_MESSAGE)
                return

            # 登録メニュー選択時
            if handler.reset_status_col == 1:
                self.reply_text_message(handler, Message.REQUEST_PRODUCT)
                return
            
            # 一覧メニュー選択時 / レシピメニュー選択時
            if handler.reset_status_col == 2 or handler.reset_status_col == 3:
                reply_message = self.return_product_list(handler)
                self.reply_flex_message(handler, reply_message)
                return

            # 登録処理 - 商品名入力時
            if handler.status.register_status == RegisterStatus.WAIT_PRODUCT:
                reply_message = self.return_datepicker(handler)
                self.reply_flex_message(handler, reply_message)
                return

        # Postbackイベント
        if handler.type == 'postback':
            # フォーマットチェック
            if super().check_invalid_postback(handler):
                self.reply_text_message(handler, Message.INVALID_POSTBACK)
                return
            
            # 登録処理
            if handler.sequence == PostbackSEQ.REGISTER_EXPIRE:
                # Datepicker入力時
                if handler.command == Command.DATEPICKER:
                    reply_message = self.return_complete_register(handler)
                    self.reply_text_message(handler, reply_message)
                    return

                # Cancel選択時
                if handler.command == Command.CANCEL:
                    self.reply_text_message(handler, Message.CANCEL)
                    return

            # 一覧処理 - 商品選択待ち
            if handler.sequence == PostbackSEQ.LIST_PRODUCT:
                # BACK / NEXT 選択時
                if handler.command == Command.BACK or handler.command == Command.NEXT:
                    reply_message = self.return_product_list(handler)
                    self.reply_flex_message(handler, reply_message)
                    return
                
                # 商品選択時
                if handler.command == Command.SELECT_PRODUCT:
                    reply_message = self.return_select_list(handler)
                    self.reply_flex_message(handler, reply_message)
                    return

            # 一覧処理 - アクション選択待ち
            if handler.sequence == PostbackSEQ.LIST_SELECT:
                # Datepicker選択時
                if handler.command == Command.CHANGE_DATE:
                    reply_message = self.return_datepicker(handler)
                    self.reply_flex_message(handler, reply_message)
                    return

                # 商品削除選択時
                if handler.command == Command.DELETE:
                    self.reply_text_message(handler, Message.DELETE)
                    return
            
            # 一覧処理 - Datepicker入力待ち
            if handler.sequence == PostbackSEQ.LIST_EXPIRE:
                # Datepicker選択時
                if handler.command == Command.DATEPICKER:
                    reply_message = self.return_complete_register(handler)
                    self.reply_text_message(handler, reply_message)
                    return

                # キャンセル選択時
                if handler.command == Command.CANCEL:
                    self.reply_text_message(handler, Message.CANCEL)
                    return

            # レシピ処理
            if handler.sequence == PostbackSEQ.RECIPE_PRODUCT:
                # BACK / NEXT / 商品選択時
                if handler.command == Command.BACK or handler.command == Command.NEXT or handler.command == Command.SELECT_PRODUCT:
                    reply_message = self.return_product_list(handler)
                    self.reply_flex_message(handler, reply_message)
                    return
                
                # レシピ検索選択時
                if handler.command == Command.SEARCH:
                    reply_message = self.return_recipe_list(handler)
                    self.reply_flex_message(handler, reply_message)
                    return

    @staticmethod
    def return_datepicker(handler):
        """return_datepicker
            * 日付選択 / Cancel の Flex Messageを作成する

        Args:
            handler(obj): handlerのインスタンス

        Returns:
           datepicker_flame(dict): messageのフォーマットを定義したJSON
        """

        # 登録処理
        if handler.type == 'message':
            sequence = PostbackSEQ.REGISTER_EXPIRE
            product_id = 0
            product_name = handler.message
        
        # 一覧処理
        if handler.type == 'postback':
            sequence = PostbackSEQ.LIST_EXPIRE
            product_id = handler.data_json['product_id']
            product_name = handler.data_json['product_name']

        # FlexMessage - header
        datepicker_flame = copy.deepcopy(Message.BUBBLE_FLAME)
        list_header = copy.deepcopy(Message.HEADER_FLAME)
        list_header['contents'][0]['text'] = product_name
        list_header['contents'][1]['text'] = "賞味期限を登録してね。"
        datepicker_flame['header'] = list_header

        # data JSONの作成 (datepicker)
        pick_data_flame = copy.deepcopy(Message.DATA_FORMAT)
        pick_data_flame['sequence'] = sequence
        pick_data_flame['command'] = Command.DATEPICKER
        pick_data_flame['product_id'] = product_id
        pick_data_flame['product_name'] = product_name
        pick_data_str = json.dumps(pick_data_flame)

        # data JSONの作成 (Cancel)
        cancel_data_flame = copy.deepcopy(pick_data_flame)
        cancel_data_flame['command'] = Command.CANCEL
        cancel_data_str = json.dumps(cancel_data_flame)

        # FlexMessage - body
        date = datetime.datetime.now()
        month = "0" + str(date.month)
        day = "0" + str(date.day)
        today_date = str(date.year) + "-" + month[-2:] + "-" + day[-2:]
    
        list_body = copy.deepcopy(Message.CALENDER_BODY)
        list_body['contents'][0]['action']['data'] = pick_data_str
        list_body['contents'][0]['action']['min'] = today_date
        list_body['contents'][1]['action']['data'] = cancel_data_str
        datepicker_flame['body'] = list_body

        # FlexMessage - style
        list_styles = copy.deepcopy(Message.COMMON_STYLES)
        datepicker_flame['styles'] = list_styles

        return datepicker_flame

    @staticmethod
    def return_complete_register(handler):
        """return_complete_register
            * 登録完了のMessageを作成する

        Args:
            handler(obj): handlerのインスタンス

        Returns:
           datepicker_flame(str): message
        """
        expire_date = handler.event.postback.params['date']
        product_name = handler.data_json['product_name']

        reply_message = Message.REGISTER_HEADER + \
                        Message.REGISTER_PRODUCT + \
                        product_name + \
                        Message.REGISTER_DATE + \
                        expire_date + \
                        Message.REGISTER_DETAIL

        return reply_message

    @staticmethod
    def return_product_list(handler):
        """return_product_list
            * 商品一覧 の Flex Messageを作成する

        Args:
            handler(obj): handlerのインスタンス

        Returns:
           list_flame(dict): messageのフォーマットを定義したJSON
        """

        # *** FlexMessage作成前提処理 *** 
        start_amount = 1
        end_amount = 5
        display_position = 0
        marker_array = []
        recipe_list = {}

        # SELECT product_id, product_name, expire_date FROM product where user_id = ? ; 
        product_list = session.query(Product.product_id, Product.product_name, Product.expire_date). \
            filter(Product.user_id == handler.user_id). \
            order_by(Product.expire_date).\
            all()
        
        # 0件の登録時
        if len(product_list) == 0:
            start_amount = 0

        # 5件以下の登録時
        if len(product_list) <= 5:
             end_amount = len(product_list)

        # Messageイベント
        if handler.type == 'message':
            # 一覧メニュー選択時
            if handler.message == MenuType.LIST:
                sequence = PostbackSEQ.LIST_PRODUCT
            
            # レシピメニュー選択時
            elif handler.message == MenuType.RECIPE:
                sequence = PostbackSEQ.RECIPE_PRODUCT
        
        # Postbackイベント
        if handler.type == 'postback':
            sequence = handler.sequence
            display_position = int(handler.data_json['display_position'])
            marker_array = handler.data_json['marker_array']

            # 共通 - Back選択時
            if handler.command == Command.BACK:
                # 表示範囲の計算
                if display_position != 0:
                    display_position -= 1
                    start_amount = display_position * 5 + 1
                    end_amount += start_amount - 1

            # 共通 - Next選択時
            if handler.command == Command.NEXT:
                # 表示範囲の計算
                if (display_position + 1) * 5 < len(product_list):
                    display_position += 1

                if len(product_list) != 0:
                    start_amount = display_position * 5 + 1
                    if start_amount + 5 > len(product_list):
                        end_amount = len(product_list)
                    else:
                        end_amount = start_amount + 4
            
            # レシピ処理 - 商品選択時
            if handler.command == Command.SELECT_PRODUCT:
                # 表示範囲の計算
                start_amount = display_position * 5 + 1
                if start_amount + 5 > len(product_list):
                    end_amount = len(product_list)
                else:
                    end_amount = start_amount + 4

                # 商品選択パターン整理
                product_id = handler.data_json['product_id']
                start_length = len(marker_array)
                
                # 商品選択 → 商品選択解除 処理
                for marker in marker_array:
                    if marker == product_id:
                        marker_array.remove(product_id)
                        break
                
                # 商品未選択 → 商品選択 処理
                if start_length == len(marker_array):
                    marker_array.append(product_id)

            # レシピ件数取得処理
            count = 0
            for marker in marker_array:
                # SELECT product_kana FROM product WHERE product_id = ? ;
                product = session.query(Product.product_kana). \
                    filter(Product.product_id == marker). \
                    first()

                # SELECT index FROM inverted_index WHERE index_kana = ? ;
                inverted_index = session.query(InvertedIndex.index). \
                    filter(InvertedIndex.index_kana == product.product_kana). \
                    first()

                # 転置インデックス配列を作成
                if inverted_index is None:
                    index_array = []
                else:
                    index_array = inverted_index.index.split(',')

                if count == 0:
                    recipe_list = set(index_array)
                else:
                    # 既に取得している転置インデックスとの積集合を取得
                    recipe_list = recipe_list.intersection(set(index_array))
                
                count += 1
        
        # *** FlexMessage作成処理 *** 
        # FlexMessage - header
        list_flame = copy.deepcopy(Message.BUBBLE_FLAME)
        list_flame['header'] = copy.deepcopy(Message.HEADER_FLAME)

        # 一覧処理
        if sequence == PostbackSEQ.LIST_PRODUCT:
            list_flame['header']['contents'][0]['text'] = '【登録商品一覧】'
            list_flame['header']['contents'][1]['text'] = '賞味期限変更 / 商品削除ができます。'

        # レシピ処理
        elif sequence == PostbackSEQ.RECIPE_PRODUCT:
            list_flame['header']['contents'][0]['text'] = '【レシピ検索】'
            list_flame['header']['contents'][1]['text'] = '検索ヒット数 : ' + str(len(recipe_list)) + '  (10件まで表示可能)'
        
        # 表示範囲から検索した商品のbodyを作成
        contents_array = []
        show_count = 0
        execution_count = 1
        color_type = ['#ff7f24', '#ff8c00', '#ffa500', '#ffb833', '#ffc966']

        for product in product_list:
            if start_amount <= execution_count <= end_amount:
                # data JSONの作成 (商品ボタン)
                body_data_flame = copy.deepcopy(Message.DATA_FORMAT)
                body_data_flame['sequence'] = sequence
                body_data_flame['command'] = Command.SELECT_PRODUCT
                body_data_flame['product_id'] = str(product.product_id)
                body_data_flame['product_name'] = product.product_name
                body_data_flame['expire_date'] = str(product.expire_date)
                body_data_flame['display_position'] = str(display_position)
                body_data_flame['marker_array'] = marker_array
                body_data_str = json.dumps(body_data_flame)
                
                # FlexMessage - body
                list_contents = copy.deepcopy(Message.LIST_CONTENTS)
                # 一覧処理
                if sequence == PostbackSEQ.LIST_PRODUCT:
                    list_contents['contents'][0]['color'] = color_type[show_count]
                
                # レシピ処理
                elif sequence == PostbackSEQ.RECIPE_PRODUCT:
                    # 商品選択時
                    if str(product.product_id) in marker_array:
                        list_contents['contents'][0]['color'] = '#ff7f24'
                    # 商品選択解除時
                    else:
                        list_contents['contents'][0]['color'] = '#ffc966'
                    
                list_contents['contents'][0]['action']['label'] = product.product_name
                list_contents['contents'][0]['action']['data'] = body_data_str
                contents_array.append(list_contents)
                show_count += 1
                
                # 1メッセージに商品は5つまで
                if show_count == 5:
                    break

            execution_count += 1

        # レシピ処理
        if sequence == PostbackSEQ.RECIPE_PRODUCT:
            # data JSON (検索ボタン)
            button_data_flame = copy.deepcopy(Message.DATA_FORMAT)
            button_data_flame['sequence'] = sequence
            button_data_flame['command'] = Command.SEARCH
            button_data_flame['marker_array'] = marker_array
            button_data_str = json.dumps(button_data_flame)

            # 検索ボタンの追加
            recipe_button = copy.deepcopy(Message.RECIPE_BUTTON)
            recipe_button['contents'][0]['action']['label'] = 'レシピを検索'
            recipe_button['contents'][0]['action']['data'] = button_data_str
            contents_array.append(recipe_button)
        
        # 商品登録件数が0件の場合は、bodyを作成しない
        if len(contents_array) != 0:
            list_body_flame = copy.deepcopy(Message.BODY_FLAME)
            list_body_flame['contents'] = contents_array
            list_flame['body'] = list_body_flame
            
        # FlexMessage - footer
        back_data_flame = copy.deepcopy(Message.DATA_FORMAT)
        # BACK ボタン
        back_data_flame['sequence'] = sequence
        back_data_flame['command'] = Command.BACK
        back_data_flame['display_position'] = str(display_position)
        back_data_flame['marker_array'] = marker_array
        back_data_str = json.dumps(back_data_flame)

        # NEXT ボタン
        next_data_flame = copy.deepcopy(back_data_flame)
        next_data_flame['command'] = Command.NEXT
        next_data_flame['marker_array'] = marker_array
        next_data_str = json.dumps(next_data_flame)
        
        # 件数表示
        list_footer = copy.deepcopy(Message.LIST_FOOTER)
        list_footer['contents'][0]['action']['data'] = back_data_str
        list_footer['contents'][1]['text'] = str(start_amount) + '-' + str(end_amount) + ' / ' + str(len(product_list))
        list_footer['contents'][2]['action']['data'] = next_data_str
    
        list_flame['footer'] = list_footer
        list_flame['styles'] = Message.COMMON_STYLES

        return list_flame

    @staticmethod
    def return_select_list(handler):
        """return_select_list
            * 商品へのアクション選択 の Flex Messageを作成する

        Args:
            handler(obj): handlerのインスタンス

        Returns:
           select_flame(dict): messageのフォーマットを定義したJSON
        """
        
        # *** FlexMessage作成前提処理 *** 
        year = handler.data_json['expire_date'][:4]
        month = handler.data_json['expire_date'][4:6]
        day = handler.data_json['expire_date'][6:8]
        expire_date = year + "-" +month + "-" + day

        product_name = handler.data_json['product_name']
        product_id = handler.data_json['product_id']

        # data JSON (datepicker)
        menu_data_flame = copy.deepcopy(Message.DATA_FORMAT)
        menu_data_flame['sequence'] = PostbackSEQ.LIST_SELECT
        menu_data_flame['command'] = 'MENU'
        menu_data_flame['product_id'] = product_id
        menu_data_flame['product_name'] = product_name

        date_data_flame = copy.deepcopy(menu_data_flame)
        date_data_flame['command'] = Command.CHANGE_DATE
        date_data_str = json.dumps(date_data_flame)

        # data JSON (delete)
        delete_data_flame = copy.deepcopy(menu_data_flame)
        delete_data_flame['command'] = Command.DELETE
        delete_data_str = json.dumps(delete_data_flame)

        # FlexMessage - header
        select_flame = copy.deepcopy(Message.BUBBLE_FLAME)
        select_header = copy.deepcopy(Message.HEADER_FLAME)
        select_header['contents'][0]['text'] = product_name
        select_header['contents'][1]['text'] = expire_date + ' に賞味期限が切れます'
        select_flame['header'] = select_header

        # FlexMessage - body
        select_body = copy.deepcopy(Message.SELECT_BODY)
        select_body['contents'][0]['contents'][0]['action']['data'] = date_data_str
        select_body['contents'][1]['contents'][0]['action']['data'] = delete_data_str
        select_flame['body'] = select_body
        select_flame['styles'] = copy.deepcopy(Message.COMMON_STYLES)

        return select_flame

    @staticmethod
    def return_recipe_list(handler):
        """return_recipe_list
            * レシピ の Flex Messageを作成する

        Args:
            handler(obj): handlerのインスタンス

        Returns:
           recipe_flame(dict): messageのフォーマットを定義したJSON
        """
        
        # レシピ候補の作成
        marker_array = marker_array = handler.data_json['marker_array']
        count = 0
        for marker in marker_array:
            # SELECT product_kana FROM product WHERE product_id = ? ;
            product = session.query(Product.product_kana). \
                filter(Product.product_id == marker). \
                first()

            # SELECT index FROM inverted_index WHERE index_kana = ? ;
            inverted_index = session.query(InvertedIndex.index). \
                filter(InvertedIndex.index_kana == product.product_kana). \
                first()

            # 転置インデックス配列を作成
            if inverted_index is None:
                index_array = []
            else:
                index_array = inverted_index.index.split(',')

            if count == 0:
                recipe_list = set(index_array)
            else:
                # 既に取得している転置インデックスとの積集合を取得
                recipe_list = recipe_list.intersection(set(index_array))
            
            count += 1

        # レシピ作成
        count = 0
        body_contents = []
        for recipe_num in recipe_list:
            # SELECT * FROM recipe WHERE recipe_number = ? ;
            recipe = session.query(Recipe). \
                filter(Recipe.recipe_number == recipe_num). \
                first()
            
            # FlexMessage - body
            recipe_body = copy.deepcopy(Message.RECIPE_BODY)
            recipe_body['header']['contents'][0]['text'] = recipe.recipe_name
            recipe_body['hero']['url'] = recipe.recipe_photo
            recipe_body['footer']['contents'][0]['action']['uri'] = recipe.recipe_url
            recipe_body['styles'] = copy.deepcopy(Message.COMMON_STYLES)
            body_contents.append(recipe_body)

            count += 1

            # 10件までの表示チェック
            if count >= 10:
                break

        recipe_flame = copy.deepcopy(Message.CAROUSEL_FLAME)
        recipe_flame['contents'] = body_contents
        
        return recipe_flame

    @staticmethod
    def reply_text_message(handler, message):
        """reply_text_message
            * messageを送信する

        Args:
            handler(obj): handlerのインスタンス
            message(str): 送信するメッセージ
        """
        token = handler.event.reply_token
        line_bot_api.reply_message(
            token, TextSendMessage(text=message))

    @staticmethod
    def reply_flex_message(handler, message):
        """reply_flex_message
            * FlexMessageを送信する

        Args:
            handler(obj): handlerのインスタンス
            message(dict): 送信するメッセージ
        """
        token = handler.event.reply_token
        line_bot_api.reply_message(
            token, FlexSendMessage(alt_text="flexMessage", contents=message))