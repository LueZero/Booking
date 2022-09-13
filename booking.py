# -*- coding: utf-8 -*-

"""
.. module:: booking.com 網站爬蟲
.. name:: zero
.. 針對 booking 高雄地區評論搜尋頁面結果，不斷去爬所有飯店評論資料
"""

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import requests
import csv
import itertools
import re
import numpy as np
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class booking():

    def __init__(self):
        # 被擋掉的參數
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        self.requests = requests
        self.BeautifulSoup = BeautifulSoup
        self.itertools = itertools
        self.re = re
        self.np = np
        return

    def get_search_page_count(self, url):

        res = self.requests.get(url)

        soupSearch = self.BeautifulSoup(res.text, 'lxml')  # 以上是網路獲取html

        # 搜尋頁面總頁數
        searchPages = soupSearch.find_all("a", class_="rlp-main-pagination__btn-txt")

        # 取搜尋頁面總頁數 跑迴圈用
        searchLastPageCount = int(searchPages[len(searchPages)-1].string)

        return searchLastPageCount

    # 跑迴圈將搜尋飯店評論的 url 整理成一維 list
    def loop_search_hotel_comments(self, url, pageCount):
        # ;offset=30&
        # 搜尋頁面，一頁30筆
        hotelNames = []
        hotelCommentUrls = []
        plusOffset = 0
        searchUrl = ""
        
        for i in range(int(pageCount)):
            if(i == 0):
                searchUrl = url
            else:
                plusOffset = plusOffset + 30
                searchUrl = url+str(";offset=")+str(plusOffset)+str("&")

            loopPageSearchGet = self.requests.get(searchUrl)

            searchResult = self.BeautifulSoup(loopPageSearchGet.text, 'lxml')  # 以上是網路獲取html

            # 搜尋頁面飯店名稱
            hotelNames.append(searchResult.find_all("a", class_="rlp-main-hotel__hotel-name-link"))

            # 搜尋頁面飯店評論 url
            hotelCommentUrls.append(searchResult.find_all("li", class_="rlp-main-hotel-review__review_link"))

        # 利用套件 itertools 合併一維 list
        return [
            list(self.itertools.chain.from_iterable(hotelCommentUrls)),
            list(self.itertools.chain.from_iterable(hotelNames)),
        ]

    # 正式爬蟲顧客對飯店的評論資訊
    def loop_formal_reptile_hotel＿comments(self, hotelComments):

        commentList = {}
        titleUrl = "https://www.booking.com/"
        key = 0
       
        # hotelComments[0] = hotel list url
        # hotelComments[1] = hotel list name 

        for url in hotelComments[0]:

            key = key + 1

            commentList[key] = []

            hotelUrl = titleUrl + str(url.a['href']) + str('?r_lang=zh-tw;rows=75&')  # all zh-tw

            try:

                # 以上是網路獲取html
                hotel = self.requests.get(hotelUrl, headers=self.headers, timeout=5)

                searchHotelResult = self.BeautifulSoup(hotel.text, 'lxml')

                # 取得飯店總評論比數
                commentTotalCountString = searchHotelResult.find("p", class_="review_list_score_count").string
                commentTotalCount = self.re.sub("\D", "", commentTotalCountString)
                
                o = []
                # 跑分頁迴圈
                for page in range(round(int(commentTotalCount)/75)):

                    if(int(page) == 0):
                        sendUrl = hotelUrl
                    else:
                        if(int(page) != 1):
                            sendUrl = hotelUrl+str(";page=")+str(int(page))
                        else:
                            continue

                    loopHotelPageRes = self.requests.get(str(sendUrl), headers=self.headers, verify=False)
                    loopHotelPageResult = self.BeautifulSoup(loopHotelPageRes.text, 'lxml')

                    print(sendUrl)

                    # 留言姓名
                    commentNames = [name.get_text().replace('\n', "").replace('\r', "") for name in loopHotelPageResult.find_all("p", class_="reviewer_name")]

                    # 國籍
                    commentCountries = [country.get_text().strip('\n') for country in loopHotelPageResult.find_all("span", class_="reviewer_country")]

                    # 留言推薦
                    commentUserReviews = [self.re.sub("\D", "", review.get_text().strip('\n')) for review in loopHotelPageResult.find_all("div", class_="review_item_user_review_count")]

                    # 評分
                    commentReviewScoreBadges = [score.get_text().replace('\n', "").replace('\r', "") for score in loopHotelPageResult.find_all("div", class_="review_item_header_score_container")]

                    # 留言標題
                    commentContentHeaders = [header.get_text().replace('\n', "").replace('\r', "") for header in loopHotelPageResult.find_all("div", class_="review_item_header_content_container")]

                    # 填寫日期
                    insertDates = [self.re.sub("\D", "", date.get_text()) for date in loopHotelPageResult.find_all("p", class_="review_item_date")]

                    # 標籤
                    infoTags = loopHotelPageResult.find_all("ul", class_="review_item_info_tags")

                    # 評語
                    commentContents = loopHotelPageResult.find_all("div", class_="review_item_review_content")

                    # 到後面沒資料停止
                    if(len(commentNames) == 0):
                        break
                    else:
                        # 迴圈跑
                        index = 0  # 跑其他list 資料index
                        for commentContent in commentContents:
                            z = len(o)  # 尋找相同陣列 key
                            # 第一次的陣列 append
                            o.append([commentNames[index]])  # 姓名
                            o[z].append(commentCountries[index])  # 國籍
                            o[z].append(commentUserReviews[index])  # 推薦數
                            o[z].append(commentReviewScoreBadges[index])  # 評分
                            o[z].append(commentContentHeaders[index])  # 留言標題
                            o[z].append(insertDates[index])  # 時間

                            # 標籤住房
                            tags = infoTags[index].find_all("li", class_='review_info_tag')
                            tagValues = [tag.get_text().replace('•', "").replace('\n', "").replace('\r', "") for tag in tags]
                            tagValue = ",".join(tagValues)
                            o[z].append(tagValue)

                            # 壞留言
                            badValue = ""
                            if(commentContent.find("p", class_='review_neg') == None):
                                badValue = ""
                            else:
                                badValue = commentContent.find("p", class_='review_neg').get_text().replace('\n', "").replace('\r', "")
                            o[z].append(badValue)

                            # 好留言
                            goodValue = ""
                            if(commentContent.find("p", class_='review_pos') == None):
                                goodValue = ""
                            else:
                                goodValue = commentContent.find("p", class_='review_pos').get_text().replace('\n', "").replace('\r', "")
                            o[z].append(goodValue)

                            index = index + 1

                commentList[key].append(o)

            except self.requests.exceptions.RequestException as e:

                print(e)

        return [commentList, [hotel.get_text() for hotel in hotelComments[1]]]


# 以搜尋結果面網址
searchUrl = "https://www.booking.com/reviews/region/kaohsiung.zh-tw.html"

if __name__ == "__main__":

    booking = booking()

    key = 0

    # 儲存路徑
    path = os.getenv("SAVE_PATH")
    
    pageCount = booking.get_search_page_count(searchUrl)
    hotelComments = booking.loop_search_hotel_comments(searchUrl, pageCount)
    result = booking.loop_formal_reptile_hotel＿comments(hotelComments)
   
    # 開始匯出 csv
    for i in result[0]:
        for data in result[0][i]:
            fileName = path + str(result[1][key]) + '.csv'
            key = key + 1
            with open(fileName, 'w', encoding="utf_8_sig", newline="") as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(["姓名", "國籍", "留言數", "評分", "留言標題", "住宿日期", "標籤", "壞留言", "好留言"])
                for lists in data:
                    writer.writerow(lists)
