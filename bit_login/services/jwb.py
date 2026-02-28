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
    
    def get_bit101_score(self, kksj=None, detailed=False):
        """获取并返回 bit101 格式的成绩数据"""
        if kksj is None: kksj = ''
        data = {
            'kksj': kksj,
            'kcxz': '',
            'kcmc': '',
            'xsfs': 'all',
        }
        response = self.session.post(f'{CONFIG["urls"]["active"]["jwb_cb"]}jsxsd/kscj/cjcx_list', data=data)
        return self.parse_bit101_score(response.text, detailed=detailed)

    def parse_bit101_score(self, data, detailed=False):
        """解析 HTML 并转化为 bit101 需要的二维数组结构"""
        parser = BeautifulSoup(data, 'html.parser')
        dataList = parser.find(id='dataList')
        if dataList is None: return []
        
        rows = dataList.find_all('tr')
        if len(rows) == 0: return []
        
        # 定义表头
        base_header = [
            "序号", "开课学期", "课程编号", "课程名称", "成绩", "成绩标识", 
            "学分", "总学时", "考试性质", "考核方式", "课程属性", "课程性质", 
            "课程归属", "课程种类", "是否第一次考试", "操作栏"
        ]
        detail_header = [
            "专业人数", "学习人数", "平均分", "本人成绩", "班级人数", "最高分", 
            "该课程所有教学班成绩录入完毕", "本人成绩在班级中占", "本人成绩在专业中占", "本人成绩在所有学生中占"
        ]
        
        header = base_header + detail_header if detailed else base_header
        res = [header]
        
        for tr in rows[1:]:
            tds = tr.find_all('td')
            row_data = [td.text.strip() for td in tds]
            
            while len(row_data) < 16:
                row_data.append("")
            row_data = row_data[:16]
            
            score = row_data[4]
            if score == '优秀': row_data[4] = '95'
            elif score == '良好': row_data[4] = '85'
            elif score == '中等': row_data[4] = '75'
            elif score == '及格': row_data[4] = '65'
            elif score == '不及格': row_data[4] = '0'
            
            if detailed:
                detail_list = [""] * 10
                a_tag = tds[-1].find('a') if len(tds) > 0 else None
                if a_tag and "onclick" in a_tag.attrs:
                    try:
                        onclick_str = a_tag["onclick"]
                        detail_url = CONFIG["urls"]["active"]["jwb_cb"] + onclick_str.split("JsMod('")[1].split("'")[0][1:]
                        detail_data = self.get_score_detail(detail_url)
                        
                        detail_list[2] = detail_data.get('average', '')
                        detail_list[5] = detail_data.get('max', '')
                        detail_list[7] = detail_data.get('class_proportion', '')
                        detail_list[8] = detail_data.get('major_proportion', '')
                        detail_list[9] = detail_data.get('school_proportion', '')
                    except Exception:
                        pass
                row_data.extend(detail_list)
                
            res.append(row_data)
            
        return res

    def get_all_bit101_score(self, detailed=False) -> list:
        """获取所有学期的 bit101 格式成绩"""
        res = self.get_bit101_score("", detailed=detailed)
        if not res: return []
        return res
    
class jwb_cjd:
    def __init__(self,session):
        self.session = session

    def get_cjd(self,gpa=True):
        require_gpa = 1 if gpa else 0
        res = self.session.get(f"https://jwb.bit.edu.cn/cjd/ScoreReport2/Index?GPA={require_gpa}").text
        if "以下显示的是本次申请的成绩信息" not in res:
            raise Exception("成绩单获取失败!")
        img_url = "https://jwb.bit.edu.cn/cjd/Temp/"+res.split("<img src=\"/cjd/Temp/")[1].split('" class="img-fluid w-100" a')[0]
        return img_url
        