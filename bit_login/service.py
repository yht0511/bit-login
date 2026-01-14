import requests
import urllib.parse
from .config import CONFIG
from .login import login, login_error

class webvpn_login:
    """WebVPN 服务"""
    def __init__(self):
        self._login = login()
    
    def login(self, username, password, session=None):
        res = self._login.login(username, password, callback_url=CONFIG["urls"]["webvpn_cb"])
        if not session: 
            session = requests.Session()
        session.cookies.update(res['cookie_json'])
        return res

class jwb_login:
    """教务系统"""
    def __init__(self):
        self._login = login()
        
    def login(self, username, password):
        res = self._login.login(username, password, callback_url=CONFIG["urls"]["jwb_cb"])
        
        headers = CONFIG["headers"]["jwb"].copy()
        headers["Referer"] = CONFIG["urls"]["jwb_referer"]
        
        self._login.session.get(res["callback"], headers=headers)
        return {
            "cookie_json": self._login.session.cookies.get_dict(),
            "cookie": "; ".join([f"{k}={v}" for k, v in self._login.session.cookies.items()])
        }
    
class jxzxehall_login:
    """教学中心/一站式大厅"""
    def __init__(self):
        self._login = login()
        
    def login(self, username, password):
        # 1. 预请求获取动态 callback
        headers = CONFIG["headers"]["jxzxehall"]
        r_pre = requests.get(CONFIG["urls"]["jxzxehall_auth"], allow_redirects=False, headers=headers)
        
        try:
            raw_service = r_pre.headers["Location"].split("?service=")[-1]
            callback_url = urllib.parse.unquote(raw_service)
        except Exception:
            raise login_error("jxzxehall: 解析 service url 失败")

        # 2. CAS 登录
        res = self._login.login(username, password, callback_url=callback_url)
        
        # 3. 必须的链式调用
        self._login.session.get(res["callback"], headers=headers)
        self._login.session.get(CONFIG["urls"]["jxzxehall_app_base"])
        self._login.session.get(CONFIG["urls"]["jxzxehall_config"], headers=headers)
        
        return {
            "cookie_json": self._login.session.cookies.get_dict(),
            "cookie": "; ".join([f"{k}={v}" for k, v in self._login.session.cookies.items()])
        }

class ibit_login:
    """iBIT 手机端聚合页"""
    def __init__(self):
        self._login = login()

    def login(self, username, password):
        data = self._login.login(username, password, callback_url=CONFIG["urls"]["ibit_cb"])
        # 尝试提取 badge
        try:
            qs = urllib.parse.urlparse(data["callback"]).query
            badge = urllib.parse.parse_qs(qs).get('badgeFromPc', [''])[0]
            if badge:
                data['cookie_json']['badge_2'] = badge
                data['cookie'] += f"; badge_2={badge}"
        except Exception:
            pass
        return data

class yanhekt_login:
    """延河课堂"""
    def __init__(self):
        self._login = login()

    def login(self, username, password):
        data = self._login.login(username, password, callback_url=CONFIG["urls"]["yanhekt_cb"])
        
        token = ""
        try:
            # 优先从 query 参数取，兜底从字符串分割取
            qs = urllib.parse.urlparse(data["callback"]).query
            token = urllib.parse.parse_qs(qs).get('token', [''])[0]
            if not token and 'token=' in data['callback']:
                token = data['callback'].split('token=')[1].split('&')[0]
        except Exception:
            pass
            
        if not token: raise login_error("Yanhekt Token 解析失败")
        
        return {
            "token": token,
            "cookie_json": data['cookie_json'],
            "cookie": data['cookie']
        }

class library_login:
    """图书馆"""
    def __init__(self):
        self._login = login()

    def login(self, username, password):
        # 1. 设置专用头
        lib_headers = CONFIG["headers"]["library"].copy()
        lib_headers.update({
            'Content-Type': CONFIG["common"]["content_type_json"],
            'Origin': CONFIG["urls"]["lib_origin"],
            'Referer': CONFIG["urls"]["lib_referer"]
        })
        self._login.session.headers.update(lib_headers)

        # 2. 预检
        try: self._login.session.get(CONFIG["urls"]["lib_cas"])
        except: pass

        # 3. 伪装 Referer 并登录
        cas_service = CONFIG["urls"]["lib_cas"]
        self._login.session.headers['Referer'] = f"{CONFIG['urls']['sso_login_ui']}?service={urllib.parse.quote(cas_service)}"
        
        # 核心登录
        data = self._login.login(username, password, callback_url=cas_service)
        
        # 4. 提取 CAS Ticket
        callback_url = data['callback']
        cas_ticket = ""
        
        # 尝试从 URL Fragment 或 Location 中提取
        if 'cas=' in callback_url:
            cas_ticket = callback_url.split('cas=')[1].split('&')[0]
        else:
            try:
                r_retry = self._login.session.get(cas_service, allow_redirects=False)
                loc = r_retry.headers.get('Location', '')
                if 'cas=' in loc: cas_ticket = loc.split('cas=')[1].split('&')[0]
            except: pass

        if not cas_ticket: raise login_error(f"图书馆登录失败: 未获取到 CAS Ticket (Url: {callback_url})")

        # 5. 换取最终 Token
        try:
            self._login.session.headers['Referer'] = CONFIG["urls"]["lib_referer"]
            resp = self._login.session.post(CONFIG["urls"]["lib_auth"], json={'cas': cas_ticket}).json()

            if resp.get("code") != 1:
                raise login_error(f"图书馆授权失败: {resp.get('msg')}")
            
            cookies = self._login.session.cookies.get_dict()
            return {
                "cookie_json": cookies,
                "cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
                "user_info": resp.get("member", {}),
                "token": resp.get("member", {}).get("token")
            }
        except Exception as e:
            raise login_error(f"图书馆 API 解析失败: {e}")

class dekt_login:
    """第二课堂"""
    def __init__(self):
        self._login = login()
        
    def login(self, username, password):
        data = self._login.login(username, password, callback_url=CONFIG["urls"]["dekt_cb"])
        self._login.session.get(data["callback"], allow_redirects=True)
        return {
            "cookie_json": self._login.session.cookies.get_dict(),
            "cookie": "; ".join([f"{k}={v}" for k, v in self._login.session.cookies.items()]),
        }