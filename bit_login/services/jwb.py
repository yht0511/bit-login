from bs4 import BeautifulSoup
from ..config import CONFIG
from datetime import datetime

def get_current_kksj():
    now = datetime.now()
    year = now.year
    if 10 <= now.month <= 12:
        semester = f"{year}-{year + 1}-1"
    if 1 <= now.month <= 3:
        semester = f"{year - 1}-{year}-1"
    if 4 <= now.month <= 9:
        semester = f"{year - 1}-{year}-2"
    return semester


class jwb:
    def __init__(self,session):
        self.session = session

    def get_score(self,kksj=None,detailed=False):
        if kksj==None: kksj = get_current_kksj()
        data = {
            'kksj': kksj,
            'kcxz': '',
            'kcmc': '',
            'xsfs': 'all',
        }
        response = self.session.post(f'{CONFIG["urls"]["active"]["jwb_cb"]}jsxsd/kscj/cjcx_list', data=data)
        res = self.parse_score(response.text,detailed=detailed)
        return res
    
    def get_score_detail(self,url):
        response = self.session.get(url)
        return self.parse_score_detail(response.text)
        
    def parse_score(self,data,detailed=False):
        parser = BeautifulSoup(data, 'html.parser')
        dataList = parser.find(id='dataList')
        if dataList is None: return
        dataList = dataList.find_all('tr')
        nameList = parser.find(id='Top1_divLoginName')
        if nameList is None: return
        student_name = nameList.text
        res=[]
        for data in dataList[1:]:
            data = data.find_all('td')
            t={
                'student':student_name,
                'course':data[3].string,
                'score':data[4].string,
                'credit':data[6].string,
                'hours':data[5].string,
                'kksj':data[1].string, 
                'type':data[11].string,
            }
            # 处理中文score
            if t['score'] == '优秀':
                t['score'] = '95'
            elif t['score'] == '良好':
                t['score'] = '85'
            elif t['score'] == '中等':
                t['score'] = '75'
            elif t['score'] == '及格':
                t['score'] = '65'
            elif t['score'] == '不及格':
                t['score'] = '0'
            # 合并
            if data[-1].find('a') and detailed:
                t.update(self.get_score_detail(CONFIG["urls"]["active"]["jwb_cb"]+data[-1].find('a')["onclick"].split("JsMod('")[1].split("'")[0][1:]))
            else:
                t.update({
                    'average': None,
                    'max': None,
                    'class_proportion': None,
                    'major_proportion': None,
                    'school_proportion': None,
                })
            res.append(t)
        return res
    
    def parse_score_detail(self,data):
        parser = BeautifulSoup(data, 'html.parser')
        dataLists = parser.find_all(id='dataList')
        class_detail=dataLists[1].find_all('tr')[-1]
        class_detail=class_detail.find_all("td")
        self_detail=dataLists[2].find_all("td")
        return {
            'average':class_detail[0].string.split("：")[-1],
            'max':class_detail[1].string.split("：")[-1],
            'class_proportion':self_detail[1].string.split("：")[-1],
            'major_proportion':self_detail[2].string.split("：")[-1],
            'school_proportion':self_detail[3].string.split("：")[-1],
        }
    
    def get_all_score(self,detailed=False)->list:
        res = self.get_score("",detailed=detailed)
        if not res: return []
        return res
    
