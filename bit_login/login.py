import requests
import re
from typing import Dict, Any
from .config import CONFIG
from .utils import convert_to_webvpn_url

class login_error(Exception):
    """BIT登录通用异常"""
    pass

class login:
    """BIT 统一身份认证核心类"""
    def __init__(self, base_url: str = ""):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CONFIG["common"]["ua"]
        })
        self.base_url = base_url if base_url else CONFIG["urls"]["base"]["sso_api"]
    
    def _get_tgt(self, username, password) -> str:
        """获取 Ticket Granting Ticket"""
        headers = {'Content-Type': CONFIG["common"]["content_type_form"]}
        
        r = self.session.post(
            self.base_url, 
            data={'username': username, 'password': password},
            headers=headers
        )
        
        if r.status_code == 401: raise login_error("登录失败: 账号或密码错误")
        if r.status_code != 201: raise login_error(f"TGT获取失败: {r.status_code}")

        tgt = r.headers.get('Location')
        if not tgt:
            match = re.search(r'action="([^"]+)"', r.text)
            if match: tgt = match.group(1)
            
        if not tgt: raise login_error("无法解析 TGT URL")
        return tgt


    def login(self, username: str, password: str, callback_url: str = "", webvpn_mode=False) -> Dict[str, Any]:
        try:
            # 1. 获取 TGT
            tgt_url = self._get_tgt(username, password)
            
            # 2. 获取 ST 
            headers = {'Content-Type': CONFIG["common"]["content_type_form"]}
            r_st = self.session.post(tgt_url, data={'service': callback_url}, headers=headers)
            
            if r_st.status_code != 200: 
                raise login_error(f"ST获取失败: {r_st.status_code}")
            
            ticket = r_st.text.strip()

            # 3. 验证 Ticket 并建立 Session
            if webvpn_mode: callback_url = convert_to_webvpn_url(callback_url)

            separator = "&" if "?" in callback_url else "?"
            final_url = f"{callback_url}{separator}ticket={ticket}"
            
            r_login = self.session.get(final_url, allow_redirects=False)
            next_url = r_login.headers.get('Location', final_url)

            return {
                "cookie_json": self.session.cookies.get_dict(),
                "cookie": "; ".join([f"{k}={v}" for k, v in self.session.cookies.items()]),
                "callback": next_url 
            }
        except requests.RequestException as e:
            raise login_error(f"网络请求异常: {e}")
        except Exception as e:
            raise login_error(f"登录异常: {e}")

