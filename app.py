from collections import UserDict
import re
from flask import Flask
from flask import request
from flask import request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,ButtonComponent,URIAction,BubbleContainer, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, StickerMessage, PostbackEvent, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, ButtonsTemplate, PostbackTemplateAction, URITemplateAction, CarouselTemplate,CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn,BoxComponent,ImageComponent,TextComponent,IconComponent,FlexSendMessage,SeparatorComponent
import pygsheets
import pandas as pd
import random
import os

app = Flask(__name__)
gc = pygsheets.authorize(service_file='seraphic-rune-257010-c3d8f5a73a95.json')
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1HmEeZN0o1lvcKNs6XSPShfNQ08qQp4TOG_DVeqE5Bsc/edit?usp=sharing')
line_bot_api = LineBotApi('TsDrCrgc+tPMls7GnC4vueh2MN0MZlSwoL4fOtFv7tgZDH8YUOaonZstYlg9sYLjFYJkP5GOYBEwrVQQI6bnsHg/izFJzwAzIjAihGXsYivd7bzuRyy/54zVlKA0M2ahmUSRWIL+1G0ruV16wRKnagdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2dee7e70d5e80b89ea5bcc8befb82405')
ws = sh.worksheet_by_title('換宿需求')
ws_value = ws.get_all_values(include_tailing_empty_rows=False)
ws_all = sh.worksheet_by_title('合併')
ws_all_value = ws_all.get_all_values(include_tailing_empty_rows=False)
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
    test = []
    print("find_all_room_last_row:",last_row)
    print("len(ws_all_value)",len(ws_all_value))
    for i in range(last_row-1,last_row-11,-1):
        #result_list += [ws_all.get_row(i)]
        print("i:",i)
        result_list += [ws_all_value[i-1]]
        print("result:",result_list,"\n")
        #print("test:",test,"\n")
    return result_list

def find_specific_room(room):
    last_row = int(next_available_row(ws_all))
    result_list = []
    print("find_specific_room_last_row:",last_row)
    for i in range(last_row-1,0,-1):
        available = ws_all_value[i-1][2]
        if available == room:
            result_list += [ws_all_value[i-1]]
            if(len(result_list)==10):
                break
    return result_list

def make_column(result_list):
    column = []
    list_len = len(result_list)
    print("list_len",list_len)
    for i in range(list_len):
        print(i," ",result_list[i][1]," ",source_worksheet(result_list[i])," ",result_list[i][2]," ",result_list[i][3]," ",result_list[i][6])
        column.append(
            CarouselColumn(
                title=result_list[i][1],
                text=source_worksheet(result_list[i])+"\n"+result_list[i][2] + result_list[i][3] + ' (樓或房號)',
                actions=[
                    MessageTemplateAction(
                        label='聯絡資訊',
                        text=result_list[i][6]
                    ),
                ]
            ))
    return column

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
        
        next_row = next_available_row(ws)
        ws.insert_rows(row =1, number = 1, values =flist)
        result_list = find_specific_room(flist[4])
        column = make_column(result_list)
        if len(column) > 0:
            sendCarousel(event,column)
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='尚無匹配房間'))
        
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def sendCarousel(event,column):  #轉盤樣板
    try:
        message = TemplateSendMessage(
            alt_text='轉盤樣板',
            template=CarouselTemplate(
                columns=column
            )
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
def get_target_id(room):
    result_list = find_specific_room(room)
    to = []
    for i in range(len(result_list)):
        to.append(result_list[i][8])
    return to

#LIFF靜態頁面
@app.route('/page')
def page():
	return render_template('index.html', liffid = liffid)

@app.route("/callback", methods = ['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)
    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'



#line_bot_api.push_message('U3ca1187f60702620e06f7e865ab6960e', TextSendMessage(text='hahahahahaha～'))
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # get user id when reply
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    mtext = event.message.text
    
                
    if mtext=='@所有房間資訊':
        #sendCarousel_all(event,result_list)
        result_list = find_all_room()
        column = make_column(result_list)
        sendCarousel(event,column)
    elif mtext[:3] == '###' and len(mtext) > 3:
        manageForm(event, mtext,user_id)
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text = reply))


if __name__=='__main__':
    app.run(debug=True)
