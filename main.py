from crawling import Crawling
from datetime import datetime
import argparse
import openpyxl

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--d", type=str, default=datetime.today().strftime("%Y%m%d"),
                      help="크롤링을 시작할 날짜, 디폴트는 오늘, 폴더명이기도 함")
    args.add_argument("--save_folder", type=str, default="C:/Users/KED/Desktop/py_project/cheonan_welfare_crawling/crawling_data",
                      help="크롤링한 데이터를 저장하는 폴더 경로(스케줄러를 이용할 시 절대경로를 사용해야 한다)")
    config = args.parse_args()

    folder = config.save_folder
    d = config.d

    crawler = Crawling()
    df = crawler.crawling()
    df.to_excel(folder+"/"+d+".xlsx",index=False,encoding="utf-8-sig")