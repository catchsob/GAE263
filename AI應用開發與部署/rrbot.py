import os
import json

from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent
)
import requests


app = Flask(__name__)


with open('env.json', encoding='utf-8') as f:
    env = json.load(f)
access_token = os.environ.get('CHANNEL_ACCESS_TOKEN', env.get('CHANNEL_ACCESS_TOKEN', ''))
secret = os.environ.get('CHANNEL_SECRET', env.get('CHANNEL_SECRET', ''))
rrapi = os.environ.get('RRAPI', env.get('RRAPI', 'http://127.0.0.1/plates'))

configuration = Configuration(access_token=access_token)
handler = WebhookHandler(secret)


def recognize_plates(image: bytes) -> list[str]:
    files = {'image': ('test.jpg', image, 'image/jpeg')}
    data = {'model': 'gemini-3.6-flash'}
    
    r = requests.post(rrapi, files=files, data=data)
    if r.status_code == 200:
        print(r.json().get('plates', []), flush=True)
        return r.json().get('plates', [])
    else:
        print(r.status_code, r.text, flush=True)
        return []


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_blob_api = MessagingApiBlob(api_client)
        content = line_bot_blob_api.get_message_content(event.message.id)
        r = recognize_plates(content)
        text = '\n'.join(r) if r else '沒車牌'
        
        line_bot_api = MessagingApi(api_client)
        
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=text)]
            )
        )


if __name__ == "__main__":
    app.run()