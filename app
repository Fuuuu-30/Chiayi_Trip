import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# 從環境變數讀取金鑰
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ---------------------------------------------------------
# 1. 行程與景點資料庫
# ---------------------------------------------------------
DAY1_TEXT = (
    "【Day 1 嘉義文青藝術之旅】\n\n"
    "09:30 嘉義火車站集合\n"
    "10:00 嘉義市立美術館\n"
    "12:30 檜意森活村（午餐＆漫步）\n"
    "15:30 阿里山森林鐵路車庫園區\n"
    "18:00 文化路夜市美食踩點\n\n"
    "💡 回覆景點名稱（如：檜意森活村）可看詳細介紹！"
)

DAY2_TEXT = (
    "【Day 2 嘉義自然與文化之旅】\n\n"
    "09:30 故宮南院\n"
    "13:00 太平雲梯（賞壯麗雲海）\n"
    "16:00 太平老街伴手禮\n"
    "18:00 賦歸\n\n"
    "💡 回覆景點名稱（如：故宮南院）可看詳細介紹！"
)

SPOTS_INFO = {
    "嘉義市立美術館": (
        "🏛️【嘉義市立美術館】\n"
        "由古蹟改建，結合古典與現代木造建築風格，極具美感！\n\n"
        "⏰ 營業時間：09:00 - 17:00 (週一公休)\n"
        "📍 地點：嘉義市西區廣州街"
    ),
    "檜意森活村": (
        "🏡【檜意森活村】\n"
        "全台最大日式官舍建築群，滿滿檜木香氣與文創店家，超好拍！\n\n"
        "⏰ 營業時間：10:00 - 18:00\n"
        "📍 必吃推薦：福義軒蛋捲"
    ),
    "文化路夜市": (
        "🍜【文化路夜市】\n"
        "嘉義夜間精華地帶！\n\n"
        "🔥 必吃名單：\n"
        "1. 林聰明沙鍋魚頭\n"
        "2. 源興御香屋（葡萄柚綠茶）\n"
        "3. 阿娥豆花"
    ),
    "故宮南院": (
        "🏺【故宮南院】\n"
        "位於太保市，擁有豐富的亞洲藝術展覽與廣闊的水景公園。\n\n"
        "⏰ 營業時間：09:00 - 17:00 (週一公休)"
    ),
    "太平雲梯": (
        "🌉【太平雲梯】\n"
        "全台海拔最高景觀吊橋，可俯瞰嘉南平原與夕陽雲海。\n\n"
        "⚠️ 建議先上網預約購票！"
    ),
}

# ---------------------------------------------------------
# 2. LINE Webhook 接收點
# ---------------------------------------------------------
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# ---------------------------------------------------------
# 3. 訊息處理邏輯
# ---------------------------------------------------------
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_msg = event.message.text.strip()

    # 判斷使用者輸入
    if user_msg in ["Day 1", "Day1", "第一天"]:
        reply_text = DAY1_TEXT
    elif user_msg in ["Day 2", "Day2", "第二天"]:
        reply_text = DAY2_TEXT
    elif user_msg in SPOTS_INFO:
        reply_text = SPOTS_INFO[user_msg]
    else:
        reply_text = (
            "你好！歡迎使用嘉義旅遊小助手 🌿\n\n"
            "請輸入以下關鍵字來查詢：\n"
            "👉 輸入「Day 1」：查看第一天行程\n"
            "👉 輸入「Day 2」：查看第二天行程\n"
            "👉 輸入景點名稱（如：檜意森活村、文化路夜市、故宮南院）：查看景點介紹"
        )

    # 發送回覆
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)],
            )
        )

if __name__ == "__main__":
    app.run(port=5000)