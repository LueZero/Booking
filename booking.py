# -*- coding: utf-8 -*-

"""
.. module:: booking.com網站爬蟲
.. name:: zero
.. 針對booking 評論搜尋頁面結果，不斷去爬所有資料
"""

from bs4 import BeautifulSoup
import requests
import csv
import itertools
import re
import numpy as np

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class booking():

    def __init__(self):
        # 被擋掉的參數
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        self.requests = requests
        self.BeautifulSoup = BeautifulSoup
        self.itertools = itertools
        self.re = re
        self.np = np
        return

    def get_search_page(self, url):

        res = self.requests.get(url)

        soup_search = self.BeautifulSoup(res.text, 'lxml')  # 以上是網路獲取html

        # 搜尋頁面總頁數
        search_page = soup_search.find_all(
            "a", class_="rlp-main-pagination__btn-txt")

        # 取搜尋頁面總頁數 跑迴圈用
        search_last_page = int(search_page[len(search_page)-1].string)

        return search_last_page

    # 跑迴圈將搜尋飯店客戶url 整理成一維 list
    def loop_page_search(self, url, page):
        # ;offset=30&
        # 搜尋頁面，一頁30筆
        hotel_name = []
        search_result_comment_url = []
        plusoffset = 0
        # int(page)
        for i in range(int(page)):
            if(i == 0):
                search_url = url
            else:
                plusoffset = plusoffset + 30
                search_url = url+str(";offset=")+str(plusoffset)+str("&")

            loop_page_search_get = self.requests.get(search_url)

            search_result = self.BeautifulSoup(
                loop_page_search_get.text, 'lxml')  # 以上是網路獲取html

            # 搜尋頁面飯店名稱
            hotel_name.append(search_result.find_all(
                "a", class_="rlp-main-hotel__hotel-name-link"))

            # 搜尋頁面擷取客戶評論url
            search_result_comment_url.append(search_result.find_all(
                "li", class_="rlp-main-hotel-review__review_link"))

        # 利用套件itertools 合併一維 list
        return [
            list(self.itertools.chain.from_iterable(search_result_comment_url)),
            list(self.itertools.chain.from_iterable(hotel_name)),
        ]

    # 正式爬蟲顧客資訊
    def loop_formal_reptile＿comment(self, url＿list):

        list_comment = {}
        title_url = "https://www.booking.com/"
        key = 0

        for url_lists in url＿list[0]:

            key = key + 1

            list_comment[key] = []

            hotel_url = title_url + \
                str(url_lists.a['href']) + \
                str('?r_lang=zh-tw;rows=75&')  # all zh-tw

            try:

                # 以上是網路獲取html
                hotel_res = self.requests.get(
                    hotel_url, headers=self.headers, timeout=5)

                search_hotel_result = self.BeautifulSoup(
                    hotel_res.text, 'lxml')
                # 取飯店總評論比數
                comment_total_count_string = search_hotel_result.find(
                    "p", class_="review_list_score_count").string
                comment_total_count = self.re.sub(
                    "\D", "", comment_total_count_string)

                o = []
                # 跑分頁迴圈
                for page in range(round(int(comment_total_count)/75)):

                    if(int(page) == 0):
                        get_url = hotel_url
                    else:
                        if(int(page) != 1):
                            get_url = hotel_url+str(";page=")+str(int(page))
                        else:
                            continue

                    loop_hotel_page_res = self.requests.get(
                        str(get_url), headers=self.headers, verify=False)
                    loop_hotel_page_result = self.BeautifulSoup(
                        loop_hotel_page_res.text, 'lxml')

                    print(get_url)

                    # 留言姓名
                    comment_name = [name.get_text().replace('\n', "").replace('\r', "") for name in loop_hotel_page_result.find_all(
                        "p", class_="reviewer_name")]

                    # 國籍
                    comment_country = [country.get_text().strip('\n') for country in loop_hotel_page_result.find_all(
                        "span", class_="reviewer_country")]

                    # 留言推薦
                    comment_user_review_count = [self.re.sub("\D", "", item_user_review_count.get_text().strip(
                        '\n')) for item_user_review_count in loop_hotel_page_result.find_all("div", class_="review_item_user_review_count")]

                    # 評分
                    comment_review_score_badge = [score_val.get_text().replace('\n', "").replace(
                        '\r', "") for score_val in loop_hotel_page_result.find_all("div", class_="review_item_header_score_container")]

                    # 留言標題
                    comment_content_container = [content_container.get_text().replace('\n', "").replace(
                        '\r', "") for content_container in loop_hotel_page_result.find_all("div", class_="review_item_header_content_container")]

                    # 填寫日期
                    insertdate = [self.re.sub("\D", "", insert_date.get_text(
                    )) for insert_date in loop_hotel_page_result.find_all("p", class_="review_item_date")]

                    # 標籤
                    tag = loop_hotel_page_result.find_all(
                        "ul", class_="review_item_info_tags")

                    # 評語
                    comment_content = loop_hotel_page_result.find_all(
                        "div", class_="review_item_review_content")

                    # 到後面沒資料停止
                    if(len(comment_name) == 0):
                        break
                    else:
                        # 迴圈跑
                        index = 0  # 跑其他list 資料index
                        for comment_contents in comment_content:
                            z = len(o)  # 尋找相同陣列 key
                            # 第一次的陣列 append
                            o.append([comment_name[index]])  # 姓名
                            o[z].append(comment_country[index])  # 國籍
                            o[z].append(
                                comment_user_review_count[index])  # 推薦數
                            o[z].append(
                                comment_review_score_badge[index])  # 評分
                            o[z].append(
                                comment_content_container[index])  # 留言標題
                            o[z].append(insertdate[index])  # 時間

                            # 標籤住房
                            tags = tag[index].find_all(
                                "li", class_='review_info_tag')
                            tag_vla_list = [tag_val.get_text().replace('•', "").replace(
                                '\n', "").replace('\r', "") for tag_val in tags]
                            tag_vla = ",".join(tag_vla_list)
                            o[z].append(tag_vla)

                            # 壞留言
                            if(comment_contents.find("p", class_='review_neg') == None):
                                bad_val = ""
                            else:
                                bad_val = comment_contents.find(
                                    "p", class_='review_neg').get_text().replace('\n', "").replace('\r', "")
                            o[z].append(bad_val)

                            # 好留言
                            if(comment_contents.find("p", class_='review_pos') == None):
                                good_val = ""
                            else:
                                good_val = comment_contents.find(
                                    "p", class_='review_pos').get_text().replace('\n', "").replace('\r', "")
                            o[z].append(good_val)

                            index = index + 1

                list_comment[key].append(o)

            except self.requests.exceptions.RequestException as e:

                print(e)

        return [list_comment, [hotel.get_text() for hotel in url＿list[1]]]


# 以搜尋結果面網址
Complete_url = "https://www.booking.com/reviews/region/kaohsiung.zh-tw.html"

if __name__ == "__main__":

    booking = booking()

    search_page = booking.get_search_page(Complete_url)
    search_comment_url = booking.loop_page_search(Complete_url, search_page)
    result = booking.loop_formal_reptile＿comment(search_comment_url)

    path = ''# 儲存路徑
    key = 0
    # 開始匯出 csv
    for i in result[0]:
        for data in result[0][i]:
            filename = path + str(result[1][key]) + '.csv'
            key = key + 1
            with open(filename, 'w', encoding="utf_8_sig", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    ["姓名", "國籍", "留言數", "評分", "留言標題", "住宿日期", "標籤", "壞留言", "好留言"])
                for lists in data:
                    writer.writerow(lists)
