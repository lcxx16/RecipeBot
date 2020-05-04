"""push.py
    * 日次(AM8:30)のJobプログラム
    * 賞味期限切れ商品の削除
    * 賞味期限間近の商品の通知
"""
from linebot import (
    LineBotApi
)

from linebot.models import (
    TextSendMessage, FlexSendMessage
)

from sqlalchemy.sql.functions import *
from setting import *
import datetime
import os

# LineApi
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

def main():
    # 今日日付
    date = datetime.datetime.now()
    today_date = str(date.year * 10000 + date.month * 100 + date.day)

    # 1週間後
    date += datetime.timedelta(days=7)
    limit_date = str(date.year * 10000 + date.month * 100 + date.day)
    
    # DELETE FROM product WHERE expire_date < ? ;
    product = session.query(Product). \
        filter(Product.expire_date < today_date). \
        delete()
    session.commit()

    # SELECT user_id FROM user WHERE status = '1'
    users = session.query(User.user_id). \
        filter(User.status == '1'). \
        all()

    for user in users:
        # SELECT product_name, expire_date FROM product 
        # WHERE user_id = ? AND expire_date < ? ORDER BY expire_date;
        products = session.query(Product.product_name, Product.expire_date). \
            filter(Product.user_id == user). \
            filter(Product.expire_date < limit_date). \
            order_by(Product.expire_date).\
            all()

        if len(products) != 0:
            expire_date = 0
            message = Message.PUSH_HEADER
            for product in products:
                if product.expire_date != expire_date:
                    expire_date = product.expire_date
                    month = str(expire_date)[4:6]
                    day = str(expire_date)[6:8]
                    message += "\n***** " + month + "月" + day + "日 *****\n"
                
                message += "■ " + product.product_name + "\n"
  
            message += Message.PUSH_FOOTER

            messages = TextSendMessage(text=message)
            line_bot_api.push_message(user.user_id, messages)


if __name__ == "__main__":
    main()



