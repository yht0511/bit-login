# bit-login 北京理工大学统一身份认证登录库

为北理工设计的统一身份认证登录模块，只需要账号密码，即可获取各个平台鉴权，直接提供 session 供使用。支持 Python 库调用和 RESTful API 服务两种方式。

## 📥 安装

```bash
git clone https://github.com/yht0511/bit-login.git
cd bit-login
pip install -r requirements.txt
```

## 🚀 快速开始 (Python SDK)

### 基础登录
```python
import bit_login

username = "your_username"
password = "your_password"

# 1. 登录 WebVPN
webvpn = bit_login.webvpn_login().login(username, password)
session = webvpn.get_session()
# 使用 session 访问校内资源
response = session.get("https://webvpn.bit.edu.cn/...")

# 2. 登录教务系统 (JWB)
jwb_login = bit_login.jwb_login().login(username, password)
# 获取成绩
scores = bit_login.jwb.jwb(jwb_login.get_session()).get_all_score()

# 3. 登录教学中心/一站式大厅 (JXZXEHALL)
hall_login = bit_login.jxzxehall_login().login(username, password)
hall_service = bit_login.jxzxehall.jxzxehall(hall_login.get_session())
# 获取学分信息
credits = hall_service.get_credit()
# 获取课程表
courses = hall_service.get_courses()

# 4. 其他服务支持
# - bit_login.ibit_login()      # iBIT
# - bit_login.yanhekt_login()   # 延河课堂
# - bit_login.library_login()   # 图书馆
```

## 🌐 RESTful API 服务

本项目提供了一个基于 FastAPI 的高性能 RESTful API 服务，支持连接池复用和自动重试，适合生产环境使用。

### 启动服务

```bash
# 启动服务器 (默认端口 8000)
bash start.sh

# 或者手动启动
gunicorn server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 接口文档

所有接口均为 POST 请求，Content-Type 为 `application/json`。

#### 通用请求参数
接口都需要携带用户的账号密码用于认证。
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

#### 1. 教务系统 - 获取成绩 (全部)
**URL**: `/api/jwb/all_score`
**参数**:
- `detailed` (bool, 可选): 是否获取详细信息

**示例**:
```bash
curl -X POST "http://localhost:8000/api/jwb/all_score" \
     -H "Content-Type: application/json" \
     -d '{"username": "...", "password": "..."}'
```

#### 2. 教务系统 - 获取成绩 (指定学期)
**URL**: `/api/jwb/score`
**参数**:
- `kksj` (string, 可选): 开课时间(学期)，如 "2023-2024-1"

#### 3. 教学中心 - 获取个人信息
**URL**: `/api/jxzxehall/student_data`

#### 4. 教学中心 - 获取学分信息
**URL**: `/api/jxzxehall/credit`

#### 5. 教学中心 - 获取课程表
**URL**: `/api/jxzxehall/courses`
**参数**:
- `kksj` (string, 可选): 学期代码

## 🛠️ 项目结构

- `bit_login/`: 核心 SDK 代码
  - `login.py`: 基础登录逻辑 (SSO)
  - `service.py`: 各个服务的登录封装
  - `services/`: 具体业务逻辑 (如教务查分、课程表)
- `server.py`: FastAPI 服务端入口
- `test.py`: SDK 测试脚本

## 🔗 参考仓库

+ https://github.com/BIT101-dev/BIT101-GO
+ https://github.com/BIT101-dev/BIT101
