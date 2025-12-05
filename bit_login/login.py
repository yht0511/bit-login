import requests
from bs4 import BeautifulSoup
from typing import  Dict
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib.parse



class login_error(Exception):
    """BIT登录异常"""
    pass


class cookie_invalid_error(login_error):
    """Cookie无效异常"""
    pass

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
    'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

class login:
    def __init__(self,base_url="https://sso.bit.edu.cn/cas/login"):
        self.base_url = base_url
        self.host = base_url.split('/')[2]
        self.session = requests.Session()
        self.session.headers.update(headers)
    
    def get_url(self, callback_url: str) -> str:
        url = self.base_url + f"?service={urllib.parse.quote(callback_url)}"
        return url
        
    def init_login(self,callback_url="") -> Dict[str, str]:
        """
        登录初始化，获取salt、execution和cookie
        """
        url = self.get_url(callback_url)
        try:
            response = self.session.get(url,headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取salt
            salt_element = soup.find(id='login-croypto')
            salt = salt_element.text if salt_element else ""
            
            # 获取execution
            execution_element = soup.find(id='login-page-flowkey')
            execution = execution_element.text if execution_element else ""
            
            # 获取cookies
            cookies = response.headers.get('Set-Cookie', '')
            
            return {
                'salt': salt,
                'execution': execution,
                'cookie': cookies
            }
            
        except requests.RequestException as e:
            raise login_error(f"webvpn init login error: {e}")
    
    def encrypt_password(self, password: str, salt: str) -> str:
        """
        加密密码 - 使用AES ECB模式加密
        """
        try:
            # Base64解码salt作为密钥
            key = base64.b64decode(salt)
            # 创建AES加密器，使用ECB模式
            cipher = AES.new(key, AES.MODE_ECB)
            # 对密码进行PKCS7填充
            padded_password = pad(password.encode('utf-8'), AES.block_size)
            # 加密
            encrypted = cipher.encrypt(padded_password)
            # 返回Base64编码的加密结果
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            raise login_error(f"密码加密失败: {e}")
    
    
    def base_login(self, username: str, password: str, execution: str, 
              cookie: str, captcha: str = "", salt: str = "",callback_url = "") -> Dict[str, str]:
        """
        执行登录并返回cookies
        """
        url = self.get_url(callback_url)
                
        # 加密密码
        encrypted_password = self.encrypt_password(password, salt)
        
        form_data = {
            'username': username,
            'password': encrypted_password,
            'execution': execution,
            'captcha_payload': captcha,
            'croypto': salt,
            'captcha_code': "",
            'type': "UsernamePassword",
            '_eventId': "submit",
            'geolocation': ""
        }
        
        _headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Origin': "https://webvpn.bit.edu.cn" if "webvpn.bit.edu.cn" in callback_url else "https://sso.bit.edu.cn",
            'Host': self.host,
            'Referrer': url,
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cookie': cookie
        }
        self.session.headers.update(_headers)
        try:
            response = self.session.post(url, data=form_data, headers=_headers, allow_redirects=False)
            # 检查是否登录成功
            if "通行密钥认证" in response.text:
                raise login_error("webvpn login error: 登录失败")
            # 返回所有cookies
            all_cookies = {}
            for cookie in self.session.cookies:
                all_cookies[cookie.name] = cookie.value
            res = {
                "cookie_json": all_cookies,
                "cookie": "; ".join([f"{name}={value}" for name, value in all_cookies.items()]),
                "callback": response.headers.get('Location', '')
            }
            return res
            
        except requests.RequestException as e:
            raise login_error(f"webvpn login error: {e}")
    
    def pre_check(self, url: str, cookie: str) -> requests.Response:
        """
        前序验证并检查cookie是否有效
        """
        try:
            headers = {'Cookie': cookie}
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            if "帐号登录或动态码登录" in response.text:
                raise cookie_invalid_error("未通过统一身份认证")
            
            return response
            
        except requests.RequestException as e:
            raise login_error(f"webvpn precheck error: {e}")
    
    def login(self, username: str, password: str, callback_url = "") -> Dict[str, str]:
        """
        完整登录流程,返回cookies及回调地址
        """
        init_data = self.init_login(callback_url)
        captcha = self.encrypt_password("{}",init_data['salt'])
        
        res = self.base_login(
            username=username,
            password=password,
            execution=init_data['execution'],
            cookie=init_data['cookie'],
            captcha=captcha,
            salt=init_data['salt'],
            callback_url=callback_url
        )
        return res


class webvpn_login:
    def __init__(self):
        self._login = login("https://webvpn.bit.edu.cn/https/77726476706e69737468656265737421e3e44ed225397c1e7b0c9ce29b5b/cas/login")
    
    def login(self,username,password,session=None):
        """
            登录并获取Cookie
            :param username: 学号
            :param password: 密码
            :return: Cookie字符串
        """
        res = self._login.login(username,password,callback_url="https://webvpn.bit.edu.cn/login?cas_login=true")
        if not session: session = requests.Session()
        session.headers.update(headers)
        session.headers.update({
            "Cookie":res['cookie']
        })
        r=session.get(res["callback"])
        if "通行密钥认证" in r.text:
            raise login_error("未成功登录!")
        res = {
            "cookie_json": session.cookies.get_dict(),
            "cookie": "; ".join([f"{k}={v}" for k, v in session.cookies.get_dict().items()]),
        }
        return res
        
        
class jwb_login:
    def __init__(self):
        self._webvpn_login = webvpn_login()
        
    def login(self,username,password):
        """
            登录并获取Cookie
            :param username: 学号
            :param password: 密码
            :return: Cookie字符串
        """
        session = requests.Session()
        cookie=self._webvpn_login.login(username, password,session)
        r=session.get("https://webvpn.bit.edu.cn/https/77726476706e69737468656265737421e3e44ed225397c1e7b0c9ce29b5b/cas/login?service=http%3A%2F%2Fjwms.bit.edu.cn%2F")
        if "通行密钥认证" in r.text:
            raise login_error("未成功登录!")
        res = {
            "cookie_json": session.cookies.get_dict(),
            "cookie": "; ".join([f"{k}={v}" for k, v in session.cookies.get_dict().items()])
        }
        return res
        
class ibit_login:
    def __init__(self):
        self._login = login()

    def login(self,username, password):
        data = self._login.login(username, password,callback_url="https://ibit.yanhekt.cn/proxy/v1/cas/callback")
        cookies = data['cookie_json']
        badge = requests.get(data["callback"],headers=headers,allow_redirects=0).headers["Location"].split("badgeFromPc=")[1]
        badge = urllib.parse.unquote(badge)
        cookies["badge_2"] = badge
        res = {
            "cookie_json": cookies,
            "cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])
        }
        return res
    

class yanhekt_login:
    def __init__(self):
        self._login = login()

    def login(self,username, password):
        data = self._login.login(username, password,callback_url="https://cbiz.yanhekt.cn/v1/cas/callback")
        cookies = data['cookie_json']
        token = requests.get(data["callback"],headers=headers,allow_redirects=0).headers["Location"].split("token=")[1].split("&")[0]
        res = {
            "token": token,
            "cookie_json": cookies,
            "cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])
        }
        return res
        

class library_login:
    """登录图书馆
    """
    def __init__(self):
        self._login = login()

    def login(self,username, password):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://seatlib.bit.edu.cn',
            'Referer': 'https://seatlib.bit.edu.cn/h5/index.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        data = self._login.login(username, password,callback_url="https://seatlib.bit.edu.cn/api/cas/cas")
        c = self._login.session.get(data["callback"],allow_redirects=0).headers
        cookies = {
            'PHPSESSID': c["Set-Cookie"].split("PHPSESSID=")[1].split(";")[0],
        }
        headers["Refer"]='https://sso.bit.edu.cn/cas/login?service=https:%2F%2Fseatlib.bit.edu.cn%2Fapi%2Fcas%2Fcas'
        response = requests.get('https://seatlib.bit.edu.cn/api/cas/cas', cookies=cookies, headers=headers,allow_redirects=0)
        cas = response.headers["Location"].split("cas=")[1]
        json_data = {
            'cas': cas
        }
        response = requests.post('https://seatlib.bit.edu.cn/api/cas/user', cookies=cookies, headers=headers, json=json_data).json()
        if response.get("code") != 1:
            raise login_error("图书馆登录失败!")
        res = {
            "cookie_json": cookies,
            "cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "user_info": response["member"],
            "token": response["member"]["token"]
        }
        return res


class dekt_login:
    """登陆第二课堂,暂时无法使用
    """
    def __init__(self):
        self._login = login()
        
    def login(self,username,password):
        """
            登录并获取Cookie
            暂时无法使用
            :param username: 学号
            :param password: 密码
            :return: Cookie字符串
        """
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://qcbldekt.bit.edu.cn',
            'Referer': 'https://qcbldekt.bit.edu.cn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        data=self._login.login(username,password,callback_url="https://qcbldekt.bit.edu.cn/cas/login")
        self._login.session.get(data["callback"],allow_redirects=1)
        res = {
            "cookie_json": self._login.session.cookies.get_dict(),
            "cookie": "; ".join([f"{k}={v}" for k, v in self._login.session.cookies.get_dict().items()]),
        }
        return res
        