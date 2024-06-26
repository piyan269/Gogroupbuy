from flask import Flask, abort, render_template, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import configparser
import git

app = Flask(__name__)

config_path = '/home/wangpython/Gogroupbuy/config.ini'

config = configparser.ConfigParser()
config.read(config_path)

line_bot_api = LineBotApi(config['line-bot']['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(config['line-bot']['CHANNEL_SECRET'])

@app.route('/git_update', methods=['POST'])
def git_update():
    repo = git.Repo('./Gogroupbuy')
    origin = repo.remotes.origin
    repo.create_head('main',
                     origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
    origin.pull()
    return '', 200

@app.route('/')
def home():
    return render_template("index.html")

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
