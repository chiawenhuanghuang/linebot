from collections import UserDict
import re
from flask import Flask
from flask import request
from flask import request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, StickerMessage, PostbackEvent, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, ButtonsTemplate, PostbackTemplateAction, URITemplateAction, CarouselTemplate, CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn
import pygsheets
import pandas as pd
import random
import os

app = Flask(__name__)
gc = pygsheets.authorize(service_file='seraphic-rune-257010-c3d8f5a73a95.json')
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1HmEeZN0o1lvcKNs6XSPShfNQ08qQp4TOG_DVeqE5Bsc/edit?usp=sharing')
line_bot_api = LineBotApi('o83yvLFWFvBC579dgcCHMloaapvZQmc7k8iHS0KUhwCmsLeTizj7al3cZTjx3qMmFYJkP5GOYBEwrVQQI6bnsHg/izFJzwAzIjAihGXsYiuvMv5kD+KUtJrnwoV0Q+LJ/XwI2CcyMNKfPqdSvuEQOwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('173dbb25ae09f18273da8ed3b3622d8c')
ws = sh.worksheet_by_title('換宿需求')
ws_value = ws.get_all_values()
ws_all = sh.worksheet_by_title('合併')
ws_all_value = ws_all.get_all_values()
#connect liff
liffid = '1655976077-m6v9W1zp'

def source_worksheet(result_list):
    if result_list[9] == "linebot登記":
        return "*linebot登記"
    return "*住宿組登記"

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.get_col(1)))
    return str(len(str_list)+1)

def find_all_room():
    last_row = int(next_available_row(ws_all))
    result_list = []
    for i in range(last_row-1,last_row-11,-1):
        result_list += [ws_all_value[i]]
    return result_list

def find_specific_room(room):
    last_row = int(next_available_row(ws_all))
    result_list = []
    for i in range(last_row-1,60,-1):
        available = ws_all_value[i][2]
        if available == room:
            result_list += [ws_all_value[i]]
    return result_list

def search(result_list):
    i = 1
    reply = "搜尋結果" + '\n\n'
    for result in result_list:
        
        #print("result:",result)
        reply += '第{}個'.format(i)  + '\n'
        reply += ' 宿舍類別：' + result[1] + '\n'
        reply += ' 宿舍：' + result[2] + '\n'
        reply += ' 樓層或房號：' + result[3] + '\n'
        reply += ' 聯絡資訊：' +  result[6] + '\n\n'
        i += 1
    return reply

#LIFF靜態頁面
@app.route('/page')
def page():
	return render_template('index.html', liffid = liffid)

@app.route("/callback", methods = ['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)
    print("bady",body)
    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#line_bot_api.push_message('U3ca1187f60702620e06f7e865ab6960e', TextSendMessage(text='hahahahahaha～'))
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    result_list = find_all_room()
    mtext = event.message.text
    if mtext=='@所有房間資訊':
        try:
            if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
                sendCarousel_all(event,result_list)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text = "不對喔孩子"))

    elif mtext[:3] == '###' and len(mtext) > 3:
        result_list = manageForm(event, mtext,user_id)
        sendCarousel_all(event,result_list)
def manageForm(event, mtext,user_id):
    try:
        flist = mtext[3:].split('/')
        text1 = '換宿類別：' + flist[0] + '\n'
        text1 += '現住宿舍類別：' + flist[1] + '\n'
        text1 += '現住宿舍：' + flist[2] + '\n'
        text1 += '現住樓層或房號：' + flist[3] + '\n'
        text1 += '想換到哪一棟宿舍：' + flist[4] + '\n'
        text1 += '想換到的樓層或房號：' + flist[5] + '\n'
        text1 += '聯絡方式：' + flist[6] + '\n'
        text1 += '特殊需求：' + flist[7]
        
        flist.append(user_id)
        flist.append("linebot登記")
        print("flist",flist)
        next_row = next_available_row(ws)
        print("next_row",next_row)
        ws.insert_rows(row =1, number = 1, values =flist)
        result_list = find_specific_room(flist[4])
        return result_list
        # list_len = len(result_list)
        # column = []
        # for i in range(list_len):
        #     column.append(
        #         CarouselColumn
        #         (
        #             title=result_list[i][1],
        #             text = source_worksheet(result_list[i][3]+"\n"+result_list[i][2] + result_list[i][3] + ' (樓或房號)'),
        #             #text = result_list[0][3],
        #             actions=[
        #                 MessageTemplateAction(
        #                     label='聯絡資訊',
        #                     text=result_list[i][6]
        #                     )

        #                 ]
                    
        #         )
        #     )
        # print("done")
        # sendCarousel_all(event,column)
        # #line_bot_api.reply_message(event.reply_token,TextSendMessage(text = reply_text))
        
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def sendCarousel_all(event,result_list):  #轉盤樣板
    try:
        column = []
        list_len = len(result_list)
        for i in range(list_len):
            column.append(
                CarouselColumn
                (
                    title=result_list[i][1],
                    text = source_worksheet(result_list[i])+"\n"+result_list[i][2] + result_list[i][3] + ' (樓或房號)',
                    #text = result_list[0][3],
                    actions=[
                        MessageTemplateAction(
                            label='聯絡資訊',
                            text=result_list[i][6],)
                        ]
                )
            )
        message = TemplateSendMessage(
            alt_text='所有房間訊息',
            template=CarouselTemplate(
                columns=column
            )
        )
        print("haha")
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def get_target_id(ws_all,room):
    result_list = find_specific_room(room)
    to = []
    for i in range(len(result_list)):
        to.append(result_list[i][8])
    return to 

if __name__=='__main__':
    app.run(debug=True)
