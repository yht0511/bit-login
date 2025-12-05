"""
BIT Login - 北京理工大学统一身份认证登录库

这个库提供了简单易用的接口来处理北京理工大学统一身份认证登录。
"""

from .login import login_error, cookie_invalid_error, login, webvpn_login, jwb_login, ibit_login, yanhekt_login, library_login

__version__ = "1.1.3"
__author__ = "Teclab"
__email__ = "admin@teclab.org.cn"
__description__ = "北京理工大学统一身份认证登录库"

__all__ = ["login_error", "cookie_invalid_error", "login", "webvpn_login", "jwb_login", "ibit_login", "yanhekt_login","library_login"]
