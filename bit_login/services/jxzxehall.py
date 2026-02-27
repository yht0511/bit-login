import uuid
import json
from datetime import datetime, timedelta
from ..config import CONFIG

TIME_TABLE = [
    [[8, 0], [8, 45]], [[8, 50], [9, 35]], [[9, 55], [10, 40]], [[10, 45], [11, 30]],
    [[11, 35], [12, 20]], [[13, 20], [14, 5]], [[14, 10], [14, 55]], [[15, 15], [16, 0]],
    [[16, 5], [16, 50]], [[16, 55], [17, 40]], [[18, 30], [19, 15]], [[19, 20], [20, 5]],
    [[20, 10], [20, 55]]
]

BUILDING_MAP = {
    "综教A": (39.733193, 116.170654), "综教B": (39.733184, 116.171878), "理教楼": (39.730116, 116.171359),
    "理学A": (39.728886, 116.171800), "理学B": (39.729267, 116.171739), "理学C": (39.729633, 116.171778),
    "文萃楼A": (39.732606, 116.174479), "文萃楼B": (39.732217, 116.174489), "文萃楼C": (39.731655, 116.174267),
    "文萃楼D": (39.731670, 116.173885), "文萃楼E": (39.731669, 116.173429), "文萃楼F": (39.732060, 116.173821),
    "文萃楼G": (39.732216, 116.173101), "文萃楼H": (39.732995, 116.173098), "文萃楼I": (39.733083, 116.173866),
    "文萃楼J": (39.733518, 116.173408), "文萃楼K": (39.733440, 116.173841), "文萃楼L": (39.733488, 116.174220),
    "文萃楼M": (39.733058, 116.174525), "良乡体育馆": (39.731844, 116.176544), "北校区篮球场": (39.736357, 116.170721),
    "南校区篮球场": (39.728026, 116.169304), "南校区排球场": (39.727381, 116.169604), "南校区足球场": (39.729583, 116.169174),
    "南校区网球场": (39.727967, 116.168370), "田径场主席台": (39.729490, 116.168474), "疏桐园A": (39.728834, 116.167727),
    "游泳馆": (39.731755, 116.177294), "化学实验中心": (39.727976, 116.170456), "工训楼": (39.726286, 116.173760),
    "西山阻燃楼": (40.037061, 116.232287), "物理实验中心": (39.729071, 116.170698)
}

def get_weeks(data):
    """根据数据获取周次列表"""
    text = data["ZCMC"]
    if "-" not in text:
        return [int(text[:-1])]
    weeks = []
    for week in text.split(","):
        start, end = week.split("-")
        if not start:
            start = week[:-1]
            end = start
        weeks += list(range(int(start), int(end.replace("周", "")) + 1))
    return weeks

def get_location(data, kch):
    """根据课程号获取上课地点"""
    for course in data:
        if course["KCH"] == kch and "JASMC" in course and course["JASMC"]:
            return course["JASMC"]
    return ""

def get_building_coord(jasmc):
    """根据教室名称关键字匹配获取坐标"""
    if not jasmc:
        return None
    keys = sorted(BUILDING_MAP.keys(), key=len, reverse=True)
    for k in keys:
        if k in jasmc:
            return BUILDING_MAP[k]
    return None

class jxzxehall:
    """教务系统相关功能操作类"""
    
    def __init__(self, session):
        """初始化"""
        self.session = session

    def get_student_data(self):
        """获取学生基础信息"""
        response = self.session.get(f'{CONFIG["urls"]["active"]["jxzxehall_app"]}/jwapp/sys/xsfacx/modules/pyfacxepg/grpyfacx.do')
        res_json = response.json()
        data = {
            "name": res_json["datas"]["grpyfacx"]["rows"][0]["XM"],
            "student_code": res_json["datas"]["grpyfacx"]["rows"][0]["XH"],
            "major": res_json["datas"]["grpyfacx"]["rows"][0]["ZYDM_DISPLAY"],
            "class": res_json["datas"]["grpyfacx"]["rows"][0]["BJDM_DISPLAY"],
            "grade": res_json["datas"]["grpyfacx"]["rows"][0]["XZNJ_DISPLAY"],
            "gender": res_json["datas"]["grpyfacx"]["rows"][0]["XBDM_DISPLAY"],
            "college": res_json["datas"]["grpyfacx"]["rows"][0]["YXDM_DISPLAY"],
            "total_credit": res_json["datas"]["grpyfacx"]["rows"][0]["ZSYQXF"],
            "completed_credit": res_json["datas"]["grpyfacx"]["rows"][0]["YWCXF"],
            "required_credit": res_json["datas"]["grpyfacx"]["rows"][0]["ZSYQXFXSZ"],
            "id": res_json["datas"]["grpyfacx"]["rows"][0]["WID"],
            "detail": {
                "pyfadm": res_json["datas"]["grpyfacx"]["rows"][0]["PYFADM"],
                "zydm": res_json["datas"]["grpyfacx"]["rows"][0]["ZYDM"],
                "xdlxdm": res_json["datas"]["grpyfacx"]["rows"][0]["XDLXDM"],
                "xdlxdm_display": res_json["datas"]["grpyfacx"]["rows"][0]["XDLXDM_DISPLAY"],
                "xbdm": res_json["datas"]["grpyfacx"]["rows"][0]["XBDM"],
                "xbdm_display": res_json["datas"]["grpyfacx"]["rows"][0]["XBDM_DISPLAY"],
                "zydm_display": res_json["datas"]["grpyfacx"]["rows"][0]["ZYDM_DISPLAY"],
                "yxdm": res_json["datas"]["grpyfacx"]["rows"][0]["YXDM"],
                "yxdm_display": res_json["datas"]["grpyfacx"]["rows"][0]["YXDM_DISPLAY"],
                "wxdm": res_json["datas"]["grpyfacx"]["rows"][0]["WID"],
                "xznj": res_json["datas"]["grpyfacx"]["rows"][0]["XZNJ"],
                "xznj_display": res_json["datas"]["grpyfacx"]["rows"][0]["XZNJ_DISPLAY"],
            }
        }
        return data
    
    def get_credit(self):
        """获取学生学分信息"""
        data = self.get_student_data()
        return {
            "total_credit": data["total_credit"],
            "completed_credit": data["completed_credit"],
            "required_credit": data["required_credit"],
        }
    
    def get_courses(self, kksj=None):
        """获取指定或当前学期课程表及排课基础数据"""
        term = kksj
        if not term:
            url = f"{CONFIG['urls']['active']['jxzxehall_app']}/jwapp/sys/wdkbby/modules/jshkcb/dqxnxq.do"
            res = self.session.get(url).json()
            term = res["datas"]["dqxnxq"]["rows"][0]["DM"]

        req_param = json.dumps({"XNXQDM": term, "ZC": "1"})
        first_day_res = self.session.post(
            f"{CONFIG['urls']['active']['jxzxehall_app']}/jwapp/sys/wdkbby/wdkbByController/cxzkbrq.do",
            data={"requestParamStr": req_param}
        ).json()
        
        first_day = ""
        for v in first_day_res.get("data", []):
            if v.get("XQ") == 1:
                first_day = v.get("RQ")
                break
        
        self.session.headers.update({
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7"
        })
        schedule_res = self.session.post(
            f"{CONFIG['urls']['active']['jxzxehall_app']}/jwapp/sys/wdkbby/modules/xskcb/cxxszhxqkb.do?vpn-12-o2-jxzxehallapp.bit.edu.cn",
            data={"XNXQDM": term}
        ).json()

        return {
            "term": term,
            "firstDay": first_day,
            "data": schedule_res["datas"]["cxxszhxqkb"]["rows"]
        }

    def generate_ics(self, kksj=None):
        """获取课程表并生成ics格式数据及统计说明"""
        schedule = self.get_courses(kksj)
        first_day = datetime.strptime(schedule["firstDay"], "%Y-%m-%d")
        class_count = 0
        time_count = 0
        
        calendar = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:BIT101 {datetime.now()}",
            "TZID:Asia/Shanghai",
            "X-WR-CALNAME:BIT101课程表"
        ]
        
        for course in schedule["data"]:
            skzc = course.get("SKZC", "")
            for week, ok in enumerate(skzc):
                if ok == '1':
                    ksjc = course.get("KSJC", 1)
                    jsjc = course.get("JSJC", 1)
                    skxq = course.get("SKXQ", 1)
                    
                    start_hm = TIME_TABLE[ksjc - 1][0]
                    end_hm = TIME_TABLE[jsjc - 1][1]
                    days_add = week * 7 + skxq - 1
                    
                    start_dt = first_day + timedelta(days=days_add, hours=start_hm[0], minutes=start_hm[1])
                    end_dt = first_day + timedelta(days=days_add, hours=end_hm[0], minutes=end_hm[1])
                    
                    jasmc = course.get('JASMC', '')
                    
                    calendar.append("BEGIN:VEVENT")
                    calendar.append(f"SUMMARY:{course.get('KCM', '')}")
                    calendar.append(f"LOCATION:{jasmc}\\n北京理工大学")
                    
                    coord = get_building_coord(jasmc)
                    if coord:
                        calendar.append(f'X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-ADDRESS="北京理工大学";X-TITLE="{jasmc}":geo:{coord[0]:.6f},{coord[1]:.6f}')
                    
                    calendar.append(f"DESCRIPTION:{course.get('SKJS', '')} | {course.get('YPSJDD', '')}")
                    calendar.append(f"DTSTART;TZID=Asia/Shanghai:{start_dt.strftime('%Y%m%dT%H%M%S')}")
                    calendar.append(f"DTEND;TZID=Asia/Shanghai:{end_dt.strftime('%Y%m%dT%H%M%S')}")
                    calendar.append(f"UID:{uuid.uuid4()}")
                    calendar.append("END:VEVENT")
                    
                    class_count += 1
                    time_count += (jsjc - ksjc + 1) * 45
        
        calendar.append("END:VCALENDAR\n")
        
        ics_content = "\n".join(calendar)
        note = f"一共添加了{schedule['term']}学期的{class_count}节课，合计坐牢时间{time_count / 60:.1f}小时（雾"
        
        return ics_content, note