import requests
from bs4 import BeautifulSoup
from typing import  Dict
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class login_error(Exception):
    """BIT登录异常"""
    pass


class cookie_invalid_error(login_error):
    """Cookie无效异常"""
    pass


class login:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def init_login(self,callback_url="") -> Dict[str, str]:
        """
        登录初始化，获取salt、execution和cookie
        """
        url = f"https://sso.bit.edu.cn/cas/login?service={callback_url}"
        print(f"正在访问登录页面: {url}")
        
        try:
            response = self.session.get(url)
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
        url = f"https://sso.bit.edu.cn/cas/login?service={callback_url}"
        
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
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Host': 'sso.bit.edu.cn',
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
        try:
            response = self.session.post(url, data=form_data, headers=headers, allow_redirects=False)
            # 检查是否登录成功
            if "帐号登录或动态码登录" in response.text:
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
        
        # 4. 执行登录
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

