from ..config import CONFIG
from datetime import datetime
import math

def get_weeks(data):
    text = data["ZCMC"]
    if "-" not in text:
        return [int(text[:-1])]
    weeks = []
    for week in text.split(","):
        start,end = week.split("-")
        if not start:
            start = week[:-1]
            end = start
        weeks += list(range(int(start),int(end.replace("周",""))+1))
    return weeks

def get_location(data,kch):
    for course in data:
        if course["KCH"]==kch and "JASMC" in course and course["JASMC"]:
            return course["JASMC"]
    return ""


class jxzxehall:
    def __init__(self,session):
        self.session = session

    def get_student_data(self):
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
        data=self.get_student_data()
        return {
            "total_credit": data["total_credit"],
            "completed_credit": data["completed_credit"],
            "required_credit": data["required_credit"],
        }
    
    def get_courses(self,kksj=None):
        print("正在获取课程表...")
        if not kksj:
            headers = {"Referer": f"{CONFIG['urls']['active']['jwb_referer']}jsxsd/framework/xsMain.jsp"}
            url = f"{CONFIG['urls']['active']['jxzxehall_app']}/jwapp/sys/wdkbby/modules/jshkcb/xnxqcx.do"
            res = self.session.get(url, headers=headers).json() # 获取学期
            DM=res["datas"]["xnxqcx"]["rows"][0]["DM"]
            print(f"选择学期:{DM}")
        else: DM = kksj
        # 获取课程
        res = self.session.post(f"{CONFIG['urls']['active']['jxzxehall_app']}/jwapp/sys/wdkbby/modules/xskcb/cxxszhxqkb.do",params={"XNXQDM":DM}).json() # 获取课程数据
        return res