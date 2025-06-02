# 北京理工大学统一身份验证登录模块

# 食用方法

登录webvpn:
```python
login_client = login.login()
# 替换为您的用户名和密码
username = "your_username"
password = "your_password"
# 登录并获取数据
data = login_client.login(username, password)
# 数据格式
# {
#     "cookie_json": {
#         "name1": "value1",
#         "name2": "value2"
#     },
#     "cookie": "cookie_string"
# }
```
登录其他网站(如延河课堂):
```python
login_client = login.login()
# 替换为您的用户名和密码
username = "your_username"
password = "your_password"
# 登录并获取数据
data = login_client.login(username, password,callback_url="https://cbiz.yanhekt.cn/v1/cas/callback")
# 数据格式
# {
#     "cookie_json": {
#         "name1": "value1",
#         "name2": "value2"
#     },
#     "cookie": "cookie_string",
#     "callback": "callback location url"
# }
# 下一步:通过回调获取延河课堂的token
# ...
```

# 参考仓库

+ https://github.com/BIT101-dev/BIT101-GO
+ https://github.com/BIT101-dev/BIT101