"""callback.py
    * LINEからのwebhookを処理する
"""
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, FollowEvent, UnfollowEvent, PostbackEvent
)
from handler import (
    MessageHandler, PostbackHandler, FollowHandler
)
from observer import (
    UserObserver, StatusObserver, ProductObserver, MessageObserver
)
from setting import *
import os

app = Flask(__name__)
line_bot_api = LineBotApi(BOT.YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(BOT.YOUR_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    """callback
        * LINEからのWebhookを受け取る
    """
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent)
def handle_message(event):
    """handle_message
        * Messageイベントの処理
    """
    event_handler = MessageHandler(event)

    status_observer = StatusObserver()
    product_observer = ProductObserver()
    message_observer = MessageObserver()

    event_handler.add_observer(product_observer)
    event_handler.add_observer(message_observer)
    event_handler.add_observer(status_observer)

    event_handler.execute()


@handler.add(PostbackEvent)
def handle_postback(event):
    """handle_postback
        * Postbackイベントの処理
    """
    event_handler = PostbackHandler(event)

    status_observer = StatusObserver()
    product_observer = ProductObserver()
    message_observer = MessageObserver()

    event_handler.add_observer(product_observer)
    event_handler.add_observer(message_observer)
    event_handler.add_observer(status_observer)

    event_handler.execute()


@handler.add(FollowEvent)
@handler.add(UnfollowEvent)
def follow(event):
    """follow
        * follow / unfollow イベントの処理
    """
    event_handler = FollowHandler(event)

    user_observer = UserObserver()
    status_observer = StatusObserver()
    message_observer = MessageObserver()

    event_handler.add_observer(user_observer)
    event_handler.add_observer(status_observer)
    event_handler.add_observer(message_observer)

    event_handler.execute()


if __name__ == "__main__":
    #    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)