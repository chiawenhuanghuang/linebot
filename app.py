from collections import UserDict
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
#print(ws)

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
        print("all:",ws_all_value[i][2])
        available = ws_all_value[i][2]
        print("available",available)
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
#connect liff
liffid = '1655976077-m6v9W1zp'

#LIFF靜態頁面
@app.route('/page')
def page():
	return render_template('index.html', liffid = liffid)

@app.route("/callback", methods = ['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)
    try:
        # ori = next_available_row(ws_all)
        # while(next_available_row(ws_all)!= ori):
        #     print("in")
        #     now = next_available_row(ws_all)-1
        #     room = ws_all.get_value('E{}'.format(now))
        #     to = get_target_id(ws_all,room)
        #     line_bot_api.push_message(to, TextSendMessage(text='有新房間'))
        #     ori = next_available_row(ws_all)
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#line_bot_api.push_message('U3ca1187f60702620e06f7e865ab6960e', TextSendMessage(text='hahahahahaha～'))
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # get user id when reply
    user_id = event.source.user_id
    #print("user_id =", user_id)
    profile = line_bot_api.get_profile(user_id)
    #print("profile",profile,type(profile))
    mtext = event.message.text
    if mtext=='@所有房間資訊':
        try:
            print("send_all")
            result_list = find_all_room()
            column = []
            list_len = len(result_list)
            for i in range(list_len):
                column.append(
                    CarouselColumn
                    (
                        title = result_list[i][1],
                        text = source_worksheet(result_list[i])+"\n"+result_list[i][2] + result_list[i][3] + ' (樓或房號)',
                        #text = result_list[0][3],
                        actions=[MessageTemplateAction(label='聯絡資訊',text=result_list[i][6]),]
                    )
                )
            print("send_all")
            sendCarousel_all(event,column)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text = "不對喔孩子"))

    elif mtext[:3] == '###' and len(mtext) > 3:
        manageForm(event, mtext,user_id)
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text = reply))
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

        #reply_text = search(result_list)
        print(result_list)
        list_len = len(result_list)
        column = []
        for i in range(list_len):
            column.append(
                CarouselColumn
                (
                    title = result_list[i][1],
                    text = source_worksheet(result_list[i])+"\n"+result_list[i][2] + result_list[i][3] + ' (樓或房號)',
                    #text = result_list[0][3],
                    actions=[MessageTemplateAction(label='聯絡資訊',text=result_list[i][6]),]
                )
            )
        #print("column",column)
        sendCarousel_all(event,column)
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text = reply_text))
        
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
def source_worksheet(result_list):
    if result_list[9] == "linebot登記":
        return "*linebot登記"
    return "*住宿組登記"

def sendCarousel_all(event,column):  #轉盤樣板
    try:
        message = TemplateSendMessage(
            alt_text='所有房間訊息',
            template=CarouselTemplate(
                columns=column
            )
        )
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


                #     CarouselColumn(
                #         title = result_list[0][1],
                #         text = source_worksheet(result_list[0])+"\n"+result_list[0][2] + result_list[0][3] + ' (樓或房號)',
                #         #text = result_list[0][3],
                #         actions=[
                #             MessageTemplateAction(
                #                 label='聯絡資訊',
                #                 text=result_list[0][6]
                #             ),
                #         ]
                #     ),
                #     CarouselColumn(
                #         # thumbnail_image_url='https://i.imgur.com/qaAdBkR.png',
                #         title=result_list[1][1],
                #         text = source_worksheet(result_list[1])+"\n"+result_list[1][2] + result_list[1][3] + ' (樓或房號)',
                #         actions=[
                #             MessageTemplateAction(
                #                 label='聯絡資訊',
                #                 text=result_list[1][6]
                #             ),
                #         ]
                #     ),
                #     CarouselColumn(
                #         # thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                #         title=result_list[2][1],
                #         text = source_worksheet(result_list[2])+"\n"+result_list[2][2] + result_list[2][3] + ' (樓或房號)',
                #         actions=[
                #             MessageTemplateAction(
                #                 label='聯絡資訊',
                #                 text=result_list[2][6]
                #             ),
                #         ]
                #     ),
                #     CarouselColumn(
                #         # thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                #         title=result_list[3][1],
                #         text = source_worksheet(result_list[3])+"\n"+result_list[3][2] + result_list[3][3] + ' (樓或房號)',
                #         #text = result_list[0][3],
                #         actions=[
                #             MessageTemplateAction(
                #                 label='聯絡資訊',
                #                 text=result_list[3][6]
                #             ),
                #         ]
                #     ),
                #     CarouselColumn(
                #         # thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                #         title=result_list[4][1],
                #         text = source_worksheet(result_list[4])+"\n"+result_list[4][2] + result_list[4][3] + ' (樓或房號)',
                #         #text = result_list[0][3],
                #         actions=[
                #             MessageTemplateAction(
                #                 label='聯絡資訊',
                #                 text=result_list[4][6]
                #             ),
                #         ]
                #     ),
                #     CarouselColumn(
                #         # thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                #         title=result_list[5][1],
                #         text = source_worksheet(result_list[5])+"\n"+result_list[5][2] + result_list[5][3] + ' (樓或房號)',
                #         #text = result_list[0][3],
                #         actions=[
                #             MessageTemplateAction(
                #                 label='聯絡資訊',
                #                 text=result_list[5][6]
                #             ),
                #         ]
                #     ),
                #     CarouselColumn(
                #         # thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                #         title=result_list[6][1],
                #         text = source_worksheet(result_list[6])+"\n"+result_list[6][2] + result_list[6][3] + ' (樓或房號)',
                #         #text = result_list[0][3],
                #         actions=[
                #             MessageTemplateAction(
                #                 label='聯絡資訊',
                #                 text=result_list[6][6]
                #             ),
                #         ]
                #     ),
                #     CarouselColumn(
                #         # thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                #         title=result_list[7][1],
                #         text = source_worksheet(result_list[7])+"\n"+result_list[7][2] + result_list[7][3] + ' (樓或房號)',
                #         #text = result_list[0][3],
                #         actions=[
                #             MessageTemplateAction(
                #                 label='聯絡資訊',
                #                 text=result_list[7][6]
                #             ),
                #         ]
                #     ),
                #     CarouselColumn(
                #         # thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                #         title=result_list[8][1],
                #         text = source_worksheet(result_list[8])+"\n"+result_list[8][2] + result_list[8][3] + ' (樓或房號)',
                #         #text = result_list[0][3],
                #         actions=[
                #             MessageTemplateAction(
                #                 label='聯絡資訊',
                #                 text=result_list[0][6]
                #             ),
                #         ]
                #     ),
                #     CarouselColumn(
                #         # thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                #         title=result_list[9][1],
                #         text = source_worksheet(result_list[9])+"\n"+result_list[9][2] + result_list[9][3] + ' (樓或房號)',
                #         #text = result_list[0][3],
                #         actions=[
                #             MessageTemplateAction(
                #                 label='聯絡資訊',
                #                 text=result_list[9][6]
                #             ),
                #         ]
                #     ),
                # ]
