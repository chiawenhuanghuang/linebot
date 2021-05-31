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
import time
import datetime # 引入datetime
nowTime = datetime.datetime.now() # 取得現在時間
# print(nowTime)

app = Flask(__name__)
gc = pygsheets.authorize(service_file='/Users/user1/Desktop/course/SAD/linebot-main/seraphic-rune-257010-c3d8f5a73a95.json')
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1HmEeZN0o1lvcKNs6XSPShfNQ08qQp4TOG_DVeqE5Bsc/edit?usp=sharing')
line_bot_api = LineBotApi('TsDrCrgc+tPMls7GnC4vueh2MN0MZlSwoL4fOtFv7tgZDH8YUOaonZstYlg9sYLjFYJkP5GOYBEwrVQQI6bnsHg/izFJzwAzIjAihGXsYivd7bzuRyy/54zVlKA0M2ahmUSRWIL+1G0ruV16wRKnagdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2dee7e70d5e80b89ea5bcc8befb82405')
ws = sh.worksheet_by_title('換宿需求')
ws_value = ws.get_all_values(include_tailing_empty_rows=False)

ws_all = sh.worksheet_by_title('合併')
ws_all_value = ws_all.get_all_values(include_tailing_empty_rows=False)
liffid = '1655976077-m6v9W1zp'
liffid_2 = '1655976077-lyGEeAwL'

def source_worksheet(result_list):
    if result_list[9] == "linebot登記":
        return "*linebot登記"
    return "*住宿組登記"

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.get_col(1)))
    return str(len(str_list)+1)

def find_all_room(which_page):
    # last_row = int(next_available_row(ws_all))
    result_list = []
    # test = []

    start = len(ws_all_value)-(which_page-1)*10-1
    for i in range(start,start-10,-1):
        result_list += [ws_all_value[i]]
    return result_list

def find_specific_room(room,roommate_d):
    last_row = len(ws_all_value)
    result_list = []
    # print("room:",room)
    room_list = room.split(',')
    roommate_d_list = roommate_d.split(',')

    #符合室友特殊需求
    for i in range(last_row-1,0,-1):
        available = ws_all_value[i][2]
        roommate_s = ws_all_value[i][7]
        for j in range(len(room_list)):
            for k in range(len(roommate_d_list)):
                if available == room_list[j] and roommate_d_list[k]==roommate_s:
                    result_list += [ws_all_value[i]]
                    if(len(result_list)==10):
                        return result_list

    #未符合室友特殊需求，但宿舍符合
    for i in range(last_row-1,0,-1):
        available = ws_all_value[i][2]
        for j in range(len(room_list)):
            if available == room_list[j]:
                result_list += [ws_all_value[i]]
                if(len(result_list)==10):
                    return result_list
                    
    return result_list

def make_column(result_list):
    column = []
    list_len = len(result_list)
    # print("list_len",list_len)
    
    for i in range(list_len):
        # print("result list:",result_list[i],"\n")
        # print(i," ",result_list[i][1]," ",source_worksheet(result_list[i])," ",result_list[i][2]," ",result_list[i][3]," ",result_list[i][6])
        if (result_list[i][3] == ""):
            result_list[i][3] = ' 未填寫'
        if (result_list[i][7] == ""):
            result_list[i][7] = '未填寫'
        column.append(
            CarouselColumn(
                title=result_list[i][1],
                text=source_worksheet(result_list[i])+"\n"+result_list[i][2] +" "+ result_list[i][3] + ' (樓或房號)\n室友：'+ result_list[i][7],
                actions=[
                    MessageTemplateAction(
                        label='聯絡資訊',
                        text=result_list[i][6]
                    ),
                ]
            ))
    return column

def make_quick_reply(all_data_num):
    item = []
    
    page_num = int((all_data_num/10)+1)
    for i in range(page_num):
        # print("result list:",result_list[i],"\n")
        # print(i," ",result_list[i][1]," ",source_worksheet(result_list[i])," ",result_list[i][2]," ",result_list[i][3]," ",result_list[i][6])
    
        item.append(
            
                QuickReplyButton(
                action=MessageAction(label="第{}頁".format(i+1), text="第{}頁".format(i+1))
                )
            
        )
    return item,page_num

def push_new_massage(new_dorm,flist):
    #last_row = int(next_available_row(ws_all))
    #print("last_row",last_row-1)
    # print("flist",flist)
    last_row = len(ws_all_value)

    userID_list = []
    for i in range(last_row-1,0,-1):
        wanted = ws_all_value[i][4]
        wanted_list = wanted.split(',')
        print("wanted_list",wanted_list)
        for j in range(len(wanted_list)):
            # print("ws_all_value[i-1][8]:",ws_all_value[i-1][8],"\n")
            # print('match:',wanted_list[j]," ",new_dorm)
            if wanted_list[j] == new_dorm and ws_all_value[i][8] != "":
                # print("inininin")
                userID_list += [ws_all_value[i][8]]
                # if(len(result_list)==10):
                #     break
    #userID_list
    column = make_column([flist])
    message = TemplateSendMessage(
            alt_text='轉盤樣板',
            template=CarouselTemplate(
                columns=column
            )
        )
    
    to_userID = list(set(userID_list))
    # print("to_userID",to_userID)

    #------移除註解------
    # for i in range(len(to_userID)):
    #     line_bot_api.push_message(to_userID[i],message)
    #------移除註解------

def manageForm(event, mtext,user_id):
    try:
        flist = mtext[3:].split('/')
        text1 = '輸入資訊'
        text1 += '現住宿舍類別：' + flist[0] + '\n'
        text1 += '現住宿舍：' + flist[1] + '\n'
        text1 += '現住樓層或房號：' + flist[2] + '\n'
        text1 += '想換到哪一棟宿舍：' + flist[3] + '\n'
        text1 += '室友或房間需求：' + flist[4] + '\n'
        text1 += '聯絡方式：' + flist[5] + '\n'
        text1 += '現任室友：' + flist[6]
        flist[5] = str(flist[5])
        print(type(flist[5]))
        nowTime = int(time.time()) # 取得現在時間
        struct_time = time.localtime(nowTime) # 轉換成時間元組
        timeString = time.strftime("%Y-%m-%d %H:%M:%S", struct_time)
        flist.insert(0,timeString)
        flist.append(user_id)
        flist.append("linebot登記")
        
        next_row = int(next_available_row(ws))-1
        ws.insert_rows(row = next_row, number = 1, values =flist)

        result_list = find_specific_room(flist[4],flist[5])
        column = make_column(result_list)
        if len(column) > 0:
            sendCarousel(event,column)
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='尚無匹配房間'))
        # print("flist:",flist," ",len(flist))
        # print("-----------------push-------------------")
        push_new_massage(flist[2],flist)

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
def search_room(event, mtext):
    try:
        flist = mtext[3:].split('/')
        text1 = '輸入資訊'
        text1 += '想換到哪一棟宿舍：' + flist[0] + '\n'
        text1 += '室友或房間需求：' + flist[1] + '\n'
        
        result_list = find_specific_room(flist[0],flist[1])
        column = make_column(result_list)
        if len(column) > 0:
            sendCarousel(event,column)
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='尚無匹配房間'))
        # print("flist:",flist," ",len(flist))
        # print("-----------------push-------------------")
        #push_new_massage(flist[2],flist)

        
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤喔！'))
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

@app.route('/search')
def search():
	return render_template('index-2.html', liffid = liffid_2)

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
    global ws_all
    ws_all = sh.worksheet_by_title('合併')
    global ws_all_value
    ws_all_value = ws_all.get_all_values(include_tailing_empty_rows=False)
                
    if mtext=='@所有房間資訊':
        all_data_num = len(ws_all_value) 
        item,page_num = make_quick_reply(all_data_num)
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
                text='選擇觀看頁數',
                quick_reply=QuickReply(
                    items=item)))


    elif mtext[:3] == '###' and len(mtext) > 3:
        manageForm(event, mtext,user_id)
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text = reply))

    elif mtext[:3] == '@@@' and len(mtext) > 3:
        search_room(event, mtext)
    elif mtext[:1]=='第':
        which_page = int(mtext[1:2])
                
        result_list = find_all_room(which_page)
        column = make_column(result_list)
        sendCarousel(event,column)
        


if __name__=='__main__':
    app.run(debug=True)
