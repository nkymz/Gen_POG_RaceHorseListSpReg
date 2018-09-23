# -*- coding: utf-8 -*-

import os
import datetime
import time

from bs4 import BeautifulSoup

from get_poh_list import get_poh_list
from get_netkeiba_session import get_netkeiba_session

PATH = os.getenv("HOMEDRIVE", "None") + os.getenv("HOMEPATH", "None") + "/Dropbox/POG/"
HTMLPATH = (PATH + "PO_race_horse_spreg_list.html").replace("\\", "/")
WEEKDAY = ["(月)", "(火)", "(水)", "(木)", "(金)", "(土)", "(日)"]

global mynow


def get_race_horse_list(horse_list):
    race_horse_list = []

    mysession = get_netkeiba_session()

    time.sleep(1)
    target_url = 'http://race.netkeiba.com/?rf=navi'
    r = mysession.get(target_url)  # requestsを使って、webから取得
    soup = BeautifulSoup(r.content, 'lxml')  # 要素を抽出

    date_list = soup.find('div', class_='DateList_Box')

    for date_item in date_list.find_all('a'):

        if date_item.get('href').split('=')[-1][0] in 'cp':
            continue

        race_mmdd = date_item.get('href').split('=')[-1][1:3] + "/" + date_item.get('href').split('=')[-1][3:5]
        race_month = int(date_item.get('href').split('=')[-1][1:3])
        race_day = int(date_item.get('href').split('=')[-1][3:5])

        date_url = 'http://race.netkeiba.com' + date_item.get('href')
        time.sleep(1)
        r = mysession.get(date_url)  # requestsを使って、webから取得
        soup = BeautifulSoup(r.text, 'lxml')  # r.contentだと文字化けする

        for i, scheduled_horse in enumerate(soup.find("table").find_all("tr")):
            if i == 0:
                continue

            element = scheduled_horse.find_all("td")

            horse_name = element[0].string
            horse_url = element[0].find("a").get("href")
            track = element[2].string[0:2]
            race_no = ("0" + element[2].string[2:])[-3:]
            race_name = element[3].string
            race_id = element[3].find("a").get("href").split("=")[-1][1:]
            race_year = int(race_id[0:4])
            race_date = race_id[0:4] + "/" + race_mmdd
            status = element[5].string

            owner = "金子真人HD"
            origin = "エラーエラーエラー"
            is_seal = False
            for horse in horse_list:
                if horse_name == horse[1]:
                    owner = horse[0].strip()
                    origin = horse[2]
                    if horse[5] == "封印":
                        is_seal = True
                    else:
                        is_seal = False

            race_url = 'http://race.netkeiba.com/?pid=race_old&id=' + "c" + race_id
            time.sleep(1)
            r = mysession.get(race_url)  # requestsを使って、webから取得
            soup = BeautifulSoup(r.content, 'lxml')  # 要素を抽出

            h1_list = soup.find_all('h1')
            race_attrib_list = h1_list[1].find_all_next('p', limit=4)
            course = race_attrib_list[0].string.strip()
            race_time = race_attrib_list[1].string[-5:]
            race_cond1 = race_attrib_list[2].string
            race_cond2 = race_attrib_list[3].string

            horse_tag = soup.find("a", href=horse_url)
            horse_row = horse_tag.find_previous("tr")
            if not horse_row.find_all('td', class_='txt_l', limit=2)[1].find('a'):
                jockey = None
            else:
                jockey = horse_row.find_all('td', class_='txt_l', limit=2)[1].find('a').string
            if not horse_row.find('td', class_='txt_r'):
                odds = None
                pop_rank = None
            else:
                odds = horse_row.find('td', class_='txt_r').string
                pop_rank = horse_row.find('td', class_='txt_r').find_next('td').string

            race_date2 = datetime.date(race_year, race_month, race_day)
            race_date = race_date + WEEKDAY[race_date2.weekday()]

            sort_key = race_date + race_time + race_no + track + horse_name

            race_horse_list.append(
                [sort_key, race_date, race_time, track, race_no, race_name, course, race_cond1, race_cond2,
                 horse_name, jockey, odds, pop_rank, race_url, horse_url, owner, origin, status, is_seal])

    race_horse_list.sort()

    return race_horse_list


def out_race_horse_list(race_horse_list):
    f = open(HTMLPATH, mode="w", encoding="utf-8")

    prev_date = None
    prev_race_no = None
    prev_race_time = None
    prev_track = None

    for i in race_horse_list:

        f.write("<!--" + str(i) + "-->\n")

        race_date = i[1]
        race_time = i[2]
        track = i[3]
        race_no = i[4]
        race_name = i[5]
        course = i[6].replace("\xa0", " ")
        race_cond2 = i[8].replace("\xa0", " ")
        horse_name = i[9]
        jockey = i[10]
        odds = i[11]
        pop_rank = i[12]
        race_url = i[13]
        horse_url = i[14]
        owner = i[15]
        origin = i[16]
        is_seal = i[18]
        sp = ' '

        status = "【特別登録】"

        s = '<h4>' + race_date + '</h4>\n'
        if prev_date is None:
            f.write(s)
        elif race_date != prev_date:
            f.write('</ul></li></ul>' + s)

        s = '<li> <a href="' + race_url + '">' + track + race_no + sp + race_name + status + '</a><br />\n'
        s2 = race_time + sp + course + sp + race_cond2 + '<br />\n<ul>'
        if not prev_date or (prev_date and race_date != prev_date):
            f.write('<ul>' + s)
            f.write(s2)
        elif race_date + race_no + race_time + track != prev_date + prev_race_no + prev_race_time + prev_track:
            f.write('</ul></li>' + s)
            f.write(s2)

        s1 = '<li> <a href="' + horse_url + '">'
        if is_seal:
            s2 = '<s>' + horse_name + '</s>'
        else:
            s2 = horse_name
        f.write(s1 + s2 + owner + '</a> <br />\n')

        f.write(origin + '<br />\n')

        if odds:
            f.write(str(odds) + '倍' + sp + str(pop_rank) + '番人気<br />\n')
        if jockey:
            f.write(jockey + '騎手<br />\n')
        f.write('</li>\n')

        prev_date = race_date
        prev_race_no = race_no
        prev_race_time = race_time
        prev_track = track

    f.write('</ul></li></ul><p>終末オーナーLOVEPOP</p>\n')

    s = str(mynow.year) + "/" + ("0" + str(mynow.month))[-2:] + "/" + ("0" + str(mynow.day))[-2:] \
        + WEEKDAY[mynow.weekday()] + " " + ("0" + str(mynow.hour))[-2:] + ":" + ("0" + str(mynow.minute))[-2:]
    f.write('<p>※' + s + ' 時点の情報より作成</p>')

    f.close()


def gen_spreg_list():
    global mynow

    mynow = datetime.datetime.today()
    out_race_horse_list(get_race_horse_list(get_poh_list()))


if __name__ == "__main__":
    gen_spreg_list()







