import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

from datetime import datetime
import time
import sys

class Crawling:
    service_type_val = {"생활안정": "NB0301", "주거-자립": "NB0302", "보육-교육": "NB0303", "고용-창업": "NB0304",
                    "보건-의료": "NB0305", "행정-안전": "NB0306", "임신-출산": "NB0307", "보호-돌봄": "NB0308",
                    "문화-환경": "NB0309", "농립축산어업": "NB0310"}  # chk-type1
    support_type_val = {"현금": "cash", "현물": "stuff", "이용권": "ticket", "서비스": "service", "기타": "etc"}  # rdo-type1
    apply_type_val = {"온라인신청": "BF0101", "타사이트신청": "BF0102", "방문신청": "BF0103",
                  "기타": "(!BF0101 !BF0102 !BF0103)"}  # rdo-type2

    post_keys = ["chk-type1","rod-type1","rdo-type2"] #상세조회용 키(서비스분야, 지원형태, 신청방법)
    super_url = "https://www.gov.kr"
    main_url = "https://www.gov.kr/portal/rcvfvrSvc/svcFind/svcSearchAll"

    now_d = datetime.today().strftime("%Y%m%d%H%M")

    size = 0
    final_return_dict = {
        "상세검색_서비스분야": [],
        "상세검색_지원형태": [],
        "상세검색_신청방법": [],

        "게시글_id": [],
        "게시글_url" : [],
        "제목": [],
        "요약": [],
        "지역상위": [],
        "지역하위": [],

        "지원형태": [],
        "신청기간": [],
        "접수기관": [],
        "전화문의": [],

        "지원대상": [],
        "선정기준": [],
        "지원내용": [],

        "신청기간": [],
        "신청방법": [],
        "제출서류": [],

        "접수기관": [],
        "문의처": [],
        # "사이트주소":None,

        "최종수정일": [],
        "스크랩시간": []
    }

    def crawling(self):
        for st in self.service_type_val:
            for supt in self.support_type_val:
                for at in self.apply_type_val:
                    page_number=0
                    while(1):
                        url_keys = ["chk-type1", "rdo-type1", "rdo-type2","startCount"]
                        url_vals = [self.service_type_val[st], self.support_type_val[supt], self.apply_type_val[at], str(page_number)]
                        url = self.get_url(self.main_url, url_keys, url_vals)

                        page = self.try_request(url)  # get요청 후 응답 수신
                        soup = bs(page.text, "html.parser")
                        posts = soup.find_all('a', {"class": "btn btn-type3"})
                        if not posts:
                            break

                        for post in posts:
                            last_url = post["href"]
                            url = self.super_url + last_url
                            print(url)

                            now_dict = {key:None for key in self.final_return_dict.keys()}
                            now_dict = self.get_post_info(url,now_dict)
                            now_dict["게시글_url"] = url
                            now_dict["게시글_id"] = last_url.split("/")[-1].split("?")[0]
                            now_dict["상세검색_서비스분야"] = st
                            now_dict["상세검색_지원형태"] = supt
                            now_dict["상세검색_신청방법"] = at
                            now_dict["상세검색_신청방법"] = at
                            now_dict["스크랩시간"] = self.now_d

                            for key,val in now_dict.items():
                                self.final_return_dict[key].append(val)
                            self.size+=1
                            print(self.size,"번째!!",now_dict)
                        page_number+=12

        print("정상종료")
        return pd.DataFrame(self.final_return_dict)

    def get_url(self,main_url,url_keys,url_vals):
        url = main_url+"?"
        size = len(url_keys)

        for i in range(size):
            url+=url_keys[i]+"="+url_vals[i]
            if i!=size-1:
                url+="&"
        return url

    def replace_text(self,text,remove_text=["\r","\n","\t","\xa0"]):
        '''
        text에 필요없는 remove_text를 제거한다
        '''
        text = text.strip()
        for r in remove_text:
            text = text.replace(r,"")

        text = text.lstrip("-").lstrip("=")
        return text

    def try_request(self,url):
        '''
        request를 수행한다. 실패시 30초 대기 후 다시 시도한다.
        '''
        for i in range(3):
            try:
                post_page = requests.get(url)
                return post_page
            except:
                print("except!")
                if i == 2:
                    sys.exit("3회 시도 실패로 강제종료")
                time.sleep(30)

    def get_post_info(self,url,now_dict):
        post_page = self.try_request(url)
        post_soup = bs(post_page.text, "html.parser")

        title = post_soup.find('strong', {"class": "benefit-detail-title"}).text
        now_dict["제목"] = title
        detail = post_soup.find('p', {"class": "benefit-detail-desc"}).text
        now_dict["요약"] = detail

        a = post_soup.find("span",{"class":"tag-item type2"})
        if a:
            now_dict["지역상위"] = post_soup.find("span", {"class": "tag-item type2"}).text
        else:
            loc = post_soup.find("span", {"class": "tag-item type1"}).text
            L = loc.split(" / ")
            assert(len(L)<=2)
            if len(L)>=2:
                now_dict["지역상위"],now_dict["지역하위"] = L[0],L[1]
            else:
                now_dict["지역상위"] = L[0]

        post_one = post_soup.find_all('li', {"class": "benefit-detail-box"})
        for po in post_one:
            k = po.span.text
            value = self.replace_text(po.p.text)
            now_dict[k] = value

        post_two = post_soup.find_all('ul', {"class": "detail-content-inner"})
        for po in post_two:
            if po.span and po.p:
                k = po.span.text
                if k == "사이트주소":
                    continue
                else:
                    value = self.replace_text(po.p.text)
                now_dict[k] = value

        post_three = post_soup.find_all('div', {"class": "detail-content-inner"})
        for po in post_three:
            if po.span.text=="문의처":
                now_dict["문의처"] = self.replace_text(po.p.text)



        last_update = post_soup.find_all("span", {"class": "last-info-cont"})[-1].text
        now_dict["최종수정일"] = last_update

        return now_dict


