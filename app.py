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
    "【嘉義之旅 Day 1】\n\n"
    "10:00 溪湖家出發\n"
    "11:00 佐登妮絲城堡（午餐）\n"
    "14:00 幸福山丘 \n"
    "16:00 住宿:偶然行旅\n"
    "(以上為開車移動) \n"
    "----------------------------------------------- \n"
    "(以下為Youbike \ 走路移動) \n"
    "16:30 榮興茶事 \n"
    "17:00 涼麵店3選1 \n"
    "17:30 文化路夜市走走 \n"
    "18:15 阿宏師火雞肉飯 \n"
    "晚上可以去百貨(秀泰、遠百)吹冷氣 \n"
    "💡 回覆景點名稱（如：檜意森活村）可看詳細介紹！"
)

DAY2_TEXT = (
    "【嘉義之旅 Day 2】\n\n"
    "09:30 飯店早餐\n"
    "10:30 臺灣花磚博物館 & 嘉義市立博物館 \n"
    "12:30 諸羅山涼麵or體育館壽司 \n"
    "13:30 興加臭豆腐 \n"
    "14:15 Daisy的雜貨店\n"
    "17:00 員林買手機\n"
    "18:00 回到溪湖家 \n\n"
    "💡 回覆景點名稱（如：故宮南院）可看詳細介紹！"
)

SPOTS_INFO = {
    SPOTS_INFO = {
    "佐登妮絲城堡": (
        "🏰【佐登妮絲城堡】\n"
        "巴洛克風格歐式城堡，擁有夢幻穹頂、歐式花園與噴泉，拍照打卡聖地！\n\n"
        "⏰ 營業時間：08:30 - 19:00\n"
        "📍 地點：嘉義縣大林鎮大埔美園區三路15號\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=佐登妮絲城堡"
    ),
    "幸福山丘": (
        "🌲【幸福山丘】\n"
        "位於山頭的貨櫃景觀餐廳，大片草皮與桐花樹，非常適合喝下午茶放鬆！\n\n"
        "⏰ 營業時間：10:00 - 18:00 (週一、二公休)\n"
        "📍 特色：手作烘焙麵包、甜點\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=幸福山丘"
    ),
    "偶然行旅": (
        "🏨【偶然行旅】\n"
        "位於嘉義市區的文青風旅店，乾淨簡約，地理位置極佳，方便逛夜市！\n\n"
        "📍 地點：嘉義市東區蘭井街167號\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=偶然行旅"
    ),
    "榮興茶事": (
        "🍵【榮興茶事】\n"
        "質感古木風茶飲專賣店，推薦特調茶飲與冷泡茶，解膩首選！\n\n"
        "⏰ 營業時間：10:00 - 20:00\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=榮興茶事"
    ),
    "文化路夜市": (
        "🍜【文化路夜市】\n"
        "嘉義夜間精華地帶，美食聚集地！\n\n"
        "🔥 必吃名單：\n"
        "1. 林聰明沙鍋魚頭\n"
        "2. 源興御香屋（葡萄柚綠茶）\n"
        "3. 阿娥豆花\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=文化路夜市"
    ),
    "阿宏師火雞肉飯": (
        "🐔【阿宏師火雞肉飯】\n"
        "在地超高人氣火雞肉飯！火雞肉片飯淋上雞油與油蔥酥，香氣十足！\n\n"
        "⏰ 營業時間：10:00 - 20:00\n"
        "📍 必點：火雞肉片飯、荷包蛋\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=阿宏師火雞肉飯"
    ),
    "臺灣花磚博物館": (
        "🏛️【臺灣花磚博物館】\n"
        "保存上千片老珍貴台灣花磚，兩層樓日式木造老屋，光影拍起來非常美！\n\n"
        "⏰ 營業時間：10:00 - 17:30 (週一、二公休)\n"
        "📍 地點：嘉義市西區林森西路256號\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=臺灣花磚博物館"
    ),
    "嘉義市立博物館": (
        "🎨【嘉義市立博物館】\n"
        "展示嘉義地質、歷史文史與桃城人文，室內吹冷氣與親子互動的好去處！\n\n"
        "⏰ 營業時間：09:00 - 17:00 (週一公休)\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=嘉義市立博物館"
    ),
    "諸羅山涼麵": (
        "🥗【諸羅山涼麵】\n"
        "嘉義在地特色美乃滋（白醋）涼麵！寬扁麵體吸附麻醬與白醋，爽口順誘人！\n\n"
        "⏰ 營業時間：06:00 - 15:00\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=諸羅山涼麵"
    ),
    "體育館壽司": (
        "🍣【體育館壽司】\n"
        "平價高 CP 值的在地台式日本料理，綜合握壽司、綜合關東煮都是熱門必點！\n\n"
        "⏰ 營業時間：11:00 - 20:00\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=體育館海鮮壽司"
    ),
    "興加臭豆腐": (
        "豆腐【興加臭豆腐】\n"
        "外皮酥脆內裡軟嫩的臭豆腐，附贈免費紅茶無限暢飲，在地熱門下午點心！\n\n"
        "⏰ 營業時間：15:00 - 00:00 (週二公休)\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=興加臭豆腐"
    ),
    "Daisy的雜貨店": (
        "☕【Daisy的雜貨店】\n"
        "老宅改造的溫馨咖啡店，滿滿古物雜貨與書香，適合悠閒享受下午茶與甜點！\n\n"
        "⏰ 營業時間：13:00 - 19:00 (週四公休)\n"
        "🗺️ 地圖：https://www.google.com/maps/search/?api=1&query=Daisy的雜貨店"
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
    if user_msg in ["Day 1", "Day1", "第一天","第一天行程"]:
        reply_text = DAY1_TEXT
    elif user_msg in ["Day 2", "Day2", "第二天","第二天行程"]:
        reply_text = DAY2_TEXT
    elif user_msg in SPOTS_INFO:
        reply_text = SPOTS_INFO[user_msg]
    else:
        reply_text = (
            "你好！歡迎使用嘉義二日遊小助手 🌿\n\n"
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
