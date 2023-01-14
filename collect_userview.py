import pandas as pd
import time
import requests
from bs4 import BeautifulSoup

restaurantsTabelogInfo = pd.read_csv("all_reviewr.csv")

count=3360

def user_scraping(reviewr_name,base_url,test_mode=False, begin_page=1, end_page=60):
    reviewr_name=reviewr_name
    reviewr_url=base_url
    store_id=''
    store_id_num=0
    store_name=''
    store_address=''
    store_genre=''
    store_tellnum=''
    store_closedday=''
    store_homepage = '',
    store_dinner_price=''
    store_lunch_price_range=''
    store_score=0
    columns=["reviewr_name","reviewr_url",'store_id','store_name','store_address','store_genre','store_tellnum','store_closedday','store_homepage','store_dinner_price_range','store_lunch_price_range','store_score']
    df = pd.DataFrame(columns=columns)
    df.to_csv("./output/user{:d}.csv".format(count) ,index=False)
    page_num = begin_page
    if test_mode:
            print("test_modeはtrueです")
            list_url = base_url +'visited_restaurants/list?PG='+str(page_num)+'&select_sort_flg=1'
            scrape_list(list_url, test_mode, reviewr_name, reviewr_url, store_id, store_id_num, store_name, store_address, store_genre, store_tellnum, store_closedday, store_homepage, store_dinner_price, store_lunch_price_range, store_score, columns)
    else:
        print("test_modeはfalseです")
        while True:
            list_url = base_url +'visited_restaurants/list?PG='+str(page_num)+'&Srt=D&SrtT=rvcn'
            print(list_url)
            if scrape_list(list_url, test_mode,reviewr_name, reviewr_url, store_id, store_id_num,store_name,store_address,store_genre,store_tellnum,store_closedday,store_homepage,store_dinner_price,store_lunch_price_range,store_score,columns) != True:
                break
            #INパラメータまでのページ数を取得する
            if page_num >= end_page:
                break
            page_num +=1
    return

def scrape_list(list_url, mode, reviewr_name, reviewr_url, store_id, store_id_num,store_name,store_address,store_genre,store_tellnum,store_closedday,store_homepage,store_dinner_price,store_lunch_price_range,store_score,columns):
    time.sleep(0.5)
    print("店舗一覧の取得")
    r =requests.get(list_url)
    print("店舗一覧の取得済み")
    if r.status_code != requests.codes.ok:
        print("店舗一覧終わり1")
        return False
    soup = BeautifulSoup(r.content, 'html.parser')
    soup_a_list = soup.find_all('a', class_='simple-rvw__rst-name-target')
    if len(soup_a_list)==0:
        print("店舗一覧終わり2")
        return False
    genre_info = soup.find_all("p",class_="simple-rvw__area-catg")
    genrelist=[]
    for genre in genre_info:
        genrelist.append(genre.text)
    if mode:
        for i, soup_a in enumerate(soup_a_list[:1]):
            item_url = soup_a.get('href') #店の個別ページURLを取得
            print('アイテムのurlは'+item_url+'です')
            store_id_num += 1
            scrape_item(item_url, mode, genrelist[i], reviewr_name, reviewr_url, store_id, store_id_num,store_name,store_address,store_genre,store_tellnum,store_closedday,store_homepage,store_dinner_price,store_lunch_price_range,store_score,columns)
    else: 
        for i, soup_a in enumerate(soup_a_list):
            item_url = soup_a.get('href') #店の個別ページURLを取得
            store_id_num +=1
            scrape_item(item_url, mode, genrelist[i], reviewr_name, reviewr_url, store_id, store_id_num,store_name,store_address,store_genre,store_tellnum,store_closedday,store_homepage,store_dinner_price,store_lunch_price_range,store_score,columns)
    return True

def scrape_item(item_url, mode, genre, reviewr_name, reviewr_url, store_id, store_id_num,store_name,store_address,store_genre,store_tellnum,store_closedday,store_homepage,store_dinner_price,store_lunch_price_range,store_score,columns):
    time.sleep(0.5)
    print("個別店舗の取得")
    r = requests.get(item_url)
    print("個別店舗の取得済")
    if r.status_code != requests.codes.ok:
        print(f'error:not found{ item_url}')
        return
    soup = BeautifulSoup(r.content, 'html.parser')
    store_name_tag = soup.find('h2', class_='display-name')
    store_name = store_name_tag.span.string
    print('店名:{}'.format(store_name.strip()))
    store_name = store_name.strip()
    # 評価点数取得
    rating_score_tag = soup.find('b', class_='c-rating__val')
    rating_score = rating_score_tag.span.string
    print('評価点数：{}点'.format(rating_score))
    store_score = rating_score
    # 店舗の住所取得
    store_address=soup.find('p',class_="rstinfo-table__address").text
    print("住所：{}".format(store_address))
    store_address = store_address
    #　店舗のジャンル取得
    store_genre=genre.replace(" ","").replace("　","").split('/')[1]
    print("ジャンル：{}".format(store_genre))
    #電話番号の取得
    try:
        store_tellnum = soup.find_all('strong', class_="rstinfo-table__tel-num")
        store_tellnum = store_tellnum[1].text
    except:
        store_tellnum = "-"
    store_tellnum=store_tellnum
    print("電話番号：{}".format(store_tellnum))
    #定休日の取得
    try:
        store_closedday = soup.find('dd', class_="rdheader-subinfo__closed-text").string
    except:
        store_closedday = ""
    store_closedday=store_closedday.replace("\n"," ").replace(' ', '').replace("\r"," ").replace("\v"," ").replace("\f"," ").replace("\x1c","").replace("\x0b","").replace("\u2028","").replace("\u2029","").replace("\u000A","")
    print("定休日：{}".format(store_closedday))
    #ホームページの取得
    try:
        store_homepage=soup.find('p', class_='homepage')
        store_homepage= store_homepage.find('span').text
    except:
        store_paymentmethod = ""
    store_homepage=store_homepage
    print("ホームページ{}".format(store_homepage))
    store_price_range_tag= soup.find_all('a', class_='rdheader-budget__price-target')
    store_dinner_price_range=store_price_range_tag[0].string
    store_lunch_price_range=store_price_range_tag[1].string
    print('  夜の予算：{}'.format(store_dinner_price_range))
    print('  昼の予算：{}'.format(store_lunch_price_range))
    store_dinner_price_range=store_dinner_price_range
    store_lunch_price_range=store_lunch_price_range
    store_df=pd.DataFrame([[reviewr_name,reviewr_url,store_id,store_name,store_address,store_genre,store_tellnum,store_closedday,store_homepage,store_dinner_price_range,store_lunch_price_range,store_score]], columns=columns)
    store_df.to_csv("output/user{:d}.csv".format(count), mode='a', header=False, index=False)

for user_data in restaurantsTabelogInfo.itertuples():
    count = count+1
    reviewr_name =user_data[1]
    reviewr_url =user_data[3]
    user_scraping(reviewr_name,reviewr_url)
    print("終了しました")
