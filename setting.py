"""setting.py
    以下を設定
    * プログラムの固定値
    * SQLAlchemyの設定
    * ORMデータオブジェクト
    * Message
"""

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import os

# ***************
#  DB
# ***************
class DB:
    URL = os.environ["DATABASE_URL"]
    
# ***************
#  LINE BOT
# ***************
class BOT:
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

# ***************
#  menu_type
# ***************
class MenuType:
    REGISTER = "登録"
    LIST = "一覧"
    RECIPE = "レシピ"

# ***************
#  status_column
# ***************
class StatusColumn:
    NONE = 0
    REGISTER = 1
    LIST = 2
    RECIPE = 3

# ***************
#  register_status
# ***************
class RegisterStatus:
    INIT = '0'
    WAIT_PRODUCT = '1'
    WAIT_DATE = '2'

# ***************
#  list_status
# ***************
class ListStatus:
    INIT = '0'
    WAIT_PRODUCT = '1'
    WAIT_SELECT = '2'
    WAIT_DATE = '3'

# ***************
#  recipe_status
# ***************
class RecipeStatus:
    INIT = '0'
    WAIT_PRODUCT = '1'

# ***************
#  postback_seq
# ***************
class PostbackSEQ:
    REGISTER_EXPIRE = '1'
    LIST_PRODUCT = '2'
    LIST_SELECT = '3'
    LIST_EXPIRE = '4'
    RECIPE_PRODUCT = '5'

# ***************
#  command
# ***************
class Command:
    DATEPICKER = 'datepicker'
    CANCEL = 'cancel'
    CHANGE_DATE = 'change'
    DELETE = 'delete'
    SEARCH = 'search'
    SELECT_PRODUCT = 'select'
    BACK = 'back'
    NEXT = 'next'


# ***************
#  楽天API設定
# ***************
class API:
    FORM = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?format=json&categoryId='
    APP = '&applicationId=1083492064762528208'

class CategoryAPI:
    FORM = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426?format=json&applicationId=1050949629223131297'

# ***************
#  SQLAlchemy
# ***************
DATABASE = DB.URL

ENGINE = create_engine(
    DATABASE,
    encoding="utf-8",
    echo=True  # True:実行時SQL発行
)

# Sessionの作成
session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=ENGINE
    )
)

Base = declarative_base()
Base.query = session.query_property()

# ***************
#  userテーブル
# ***************
class User(Base):
    __tablename__ = 'user'
    user_id = Column('user_id', String(33), primary_key=True)
    user_name = Column('user_name', String(20))
    user_photo = Column('user_photo', Text)
    register_date = Column('register_date', Integer)
    status = Column('status', String(1), default='1')
    delete_date = Column('delete_date', Integer, default=0)

# ***************
#  statusテーブル
# ***************
class Status(Base):
    __tablename__ = "status"
    user_id = Column('user_id', String(33), primary_key=True)
    register_status = Column('register_status', String(1), default='0')
    list_status = Column('list_status', String(1), default='0')
    recipe_status = Column('recipe_status', String(1), default='0')
    web_status = Column('web_status', String(1), default='0')

# ***************
#  productテーブル
# ***************
class Product(Base):
    __tablename__ = "product"
    product_id = Column('product_id', Integer, primary_key=True)
    product_name = Column('product_name', String(15))
    product_kana = Column('product_kana', String(30))
    user_id = Column('user_id', String(33))
    register_date = Column('register_date', Integer)
    expire_date = Column('expire_date', Integer)
    status = Column('status', String(1), default='1')

# ***************
#  recipeテーブル
# ***************
class Recipe(Base):
    __tablename__ = "recipe"
    recipe_number = Column('recipe_number', Integer, primary_key=True)
    recipe_id = Column('recipe_id', Integer)
    recipe_name = Column('recipe_name', String(50))
    recipe_url = Column('recipe_url', Text)
    recipe_photo = Column('recipe_photo', Text)
    material = Column('material', Text)
    large_id = Column('large_id', Integer)
    medium_id = Column('medium_id', Integer)
    small_id = Column('small_id', Integer)
    register_date = Column('register_date', Integer)

# ***************
#  inverted_indexテーブル
# ***************
class InvertedIndex(Base):
    __tablename__ = "inverted_index"
    index_id = Column('index_id', Integer, primary_key=True)
    index_name = Column('index_name', String(30))
    index_kana = Column('index_kana', String(30))
    index_category = Column('index_category', String(20))
    index = Column('index', Text)

# ***************
#  categoryテーブル
# ***************
class Category(Base):
    __tablename__ = "category"
    category = Column('category', String(1))
    category_id = Column('category_id', Integer, primary_key=True)
    category_name = Column('category_name', String(30))
    category_url = Column('category_url', Text)
    parent_category = Column('parent_category', String(1))

# ***************
#  category_allビュー
# ***************
class CategoryAll(Base):
    __tablename__ = "category_all"
    large_id = Column('large_id', Integer, primary_key=True)
    large_name = Column('large_name', String(30))
    large_url = Column('large_url', Text)
    medium_id = Column('medium_id', Integer, primary_key=True)
    medium_name = Column('medium_name', String(30))
    medium_url = Column('medium_url', Text)
    small_id = Column('small_id', Integer, primary_key=True)
    small_name = Column('small_name', String(30))
    small_url = Column('small_url', Text)

# ***************
# 　Message
# ***************
class Message:
    USER_REGISTER = "友達登録ありがとう！\n" + \
                    "メニューから操作を選んでね！\n\n" + \
                    "■ 登録\n" + \
                    "商品の登録ができます\n\n" + \
                    "■ 一覧\n" + \
                    "賞味期限の変更 / 商品削除ができます\n\n" + \
                    "■ レシピ\n" + \
                    "レシピを検索できます\n\n" + \
                    "■ 通知機能\n" + \
                    "賞味期限が近い商品があればAM8:30に通知します"
    REQUEST_PRODUCT = "登録したい商品を1つ入力してね。"
    REQUEST_DATEPICKER = "日付を選択するか、キャンセルボタンを押してね"
    INVALID_POSTBACK = "そのボタンは今使えないよ。もう一度メニューから操作を選んでみよう。"
    CANCEL = "キャンセルしました。また登録したいときは下のボタンから選んでね。"
    DELETE = "削除しました。もう一度登録したいときは、下のメニューから操作してね。"
    NO_RECIPE = "レシピが見つかりませんでした。"
    NOT_AVAILABLE = "その機能はまだ有効になっていません。"
    ERROR = "エラーが発生したよ。管理者に相談してみよう。"

    INVALID_MESSAGE = "そのメッセージはわからないよ。下のメニューから操作を開始してね"

    REGISTER_HEADER = "以下の内容で登録したよ。\n\n"
    REGISTER_PRODUCT = "■ 商品名\n"
    REGISTER_DATE = "\n\n■ 賞味期限\n"
    REGISTER_DETAIL = "\n\n賞味期限が1週間を切ったら、AM8:30頃に通知するよ。"

    PUSH_HEADER = "【賞味期限1週間通知】\n"
    PUSH_FOOTER = "\nこの食材で作れる料理は、下のメニューの[レシピ]から探してみてね\n\n" + \
                    "※賞味期限が切れると自動的に商品が削除されるよ。"

    # carouselのtemplate flame
    CAROUSEL_FLAME = {
        "type": "carousel"
    }

    # bubbleのtemplate flame
    BUBBLE_FLAME = {
        "type": "bubble"
    }

    # headerのフレーム
    HEADER_FLAME = {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
            "type": "text",
            "text": "$replace_str$"
            },
            {
            "type": "text",
            "text": "$replace_str$",
            "size": "xs"
            }
        ]
    }

    # bodyのフレーム
    BODY_FLAME = {
        "type": "box",
        "layout": "vertical",
        "contents": []
    }

    # 共通スタイル
    COMMON_STYLES = {
        "header": {
            "backgroundColor": "#fdd35c"
        },
        "body": {
            "backgroundColor": "#ffedab"
        },
        "footer": {
            "backgroundColor": "#fdd35c"
        }
    }

    # Datepickerのフォーマット
    CALENDER_BODY = {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {
                "type": "button",
                "action": {
                    "type": "datetimepicker",
                    "label": "日付 入力",
                    "mode": "date",
                    "data": '$replace_str$',
                    "min": '$replace_str$'
                },
                "style": "primary",
                "height": "sm",
                "gravity": "center",
                "position": "relative",
                "color": "#ff8c00",
                "offsetEnd": "5px"
            },
            {
                "type": "button",
                "action": {
                    "type": "postback",
                    "label": "Cancel",
                    "data": '$replace_str$'
                },
                "color": "#ffa500",
                "style": "primary",
                "height": "sm",
                "position": "relative",
                "offsetStart": "5px"
            }
        ]
    }

    # 商品一覧フォーマット
    LIST_CONTENTS = {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "button",
                "action": {
                    "type": "postback",
                    "label": "$replace_text$",
                    "data": "$replace_text$"
                },
                "color": "#ff8c00",
                "style": "primary",
                "position": "relative",
                "margin": "none",
                "height": "sm"
            }
        ],
        "height": "40px",
        "margin": "md"
    }

    # レシピのSEARCHボタン
    RECIPE_BUTTON = {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "$replace_str$",
              "data": "$replace_str$"
            },
            "color": "#ff6347",
            "style": "primary",
            "position": "relative",
            "margin": "none",
            "height": "sm"
          }
        ],
        "height": "40px",
        "margin": "md",
        "cornerRadius": "30px"
      }

    # 商品一覧のfooterフォーマット
    LIST_FOOTER = {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {
                "type": "text",
                "text": "<< Back",
                "align": "start",
                "color": "#0075c2",
                "action": {
                    "type": "postback",
                    "label": "<< Back",
                    "data": "SEQ2BACKX"
                }
            },
            {
                "type": "text",
                "text": "0/0",
                "align": "center"
            },
            {
                "type": "text",
                "text": "Next >>",
                "align": "end",
                "color": "#ea5550",
                "action": {
                    "type": "postback",
                    "label": "Next >>",
                    "data": "SEQ2NEXTX"
                }
            }
        ]
    }

    # アクション選択のフォーマット
    SELECT_BODY = {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "button",
                "action": {
                "type": "postback",
                "label": "賞味期限を変更する",
                "data": "$replace_str$"
                },
                "color": "#ffa500",
                "style": "primary",
                "position": "relative",
                "margin": "none",
                "height": "sm"
            }
            ],
            "height": "40px",
            "margin": "md"
        },
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "button",
                "action": {
                "type": "postback",
                "data": "$replace_str$",
                "label": "商品を削除する"
                },
                "color": "#f4a460",
                "style": "primary",
                "position": "relative",
                "margin": "none",
                "height": "sm"
            }
            ],
            "height": "40px",
            "margin": "md"
        }
        ]
    }

    # data JSON の templateフォーマット
    DATA_FORMAT = {
        "sequence": "$replace_str$",
        "command": "$replace_str$"
    }

    # レシピのフォーマット
    RECIPE_BODY = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": "$replace_str$",
                "weight": "bold"
            }
            ]
        },
        "hero": {
            "type": "image",
            "url": "$replace_str$",
            "size": "full",
            "aspectMode": "cover"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "button",
                "action": {
                "type": "uri",
                "label": "詳細を確認する",
                "uri": "$replace_str$"
                },
                "height": "sm",
                "style": "primary",
                "color": "#ffa500"
            }
            ]
        }
    }