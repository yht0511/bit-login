CONFIG = {
    "common": {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "content_type_form": "application/x-www-form-urlencoded",
        "content_type_json": "application/json"
    },
    "urls": {
        "sso_api": "https://sso.bit.edu.cn/cas/v1/tickets",
        "sso_login_ui": "https://sso.bit.edu.cn/cas/login",
        "webvpn_cb": "https://sso.bit.edu.cn/cas/login",
        "jwb_cb": "http://jwms.bit.edu.cn/",
        "jwb_referer": "https://jwms.bit.edu.cn/",
        "ibit_cb": "https://ibit.yanhekt.cn/proxy/v1/cas/callback",
        "yanhekt_cb": "https://cbiz.yanhekt.cn/v1/cas/callback",
        "dekt_cb": "https://qcbldekt.bit.edu.cn/cas/login",
        "jxzxehall_auth": "https://jxzxehall.bit.edu.cn/auth-protocol-core/login?service=https%3A%2F%2Fjxzxehallapp.bit.edu.cn%2Fjwapp%2Fsys%2Fxsfacx%2F*default%2Findex.do",
        "jxzxehall_app_base": "https://jxzxehallapp.bit.edu.cn/jwapp/sys/xsfacx/*default/index.do",
        "jxzxehall_config": "https://jxzxehallapp.bit.edu.cn/jwapp/sys/funauthapp/api/getAppConfig/xsfacx-4766859113956613.do?v=08260885168155102",
        "lib_cas": "https://seatlib.bit.edu.cn/api/cas/cas",
        "lib_auth": "https://seatlib.bit.edu.cn/api/cas/user",
        "lib_referer": "https://seatlib.bit.edu.cn/h5/index.html",
        "lib_origin": "https://seatlib.bit.edu.cn"
    },
    "headers": {
        "jwb": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Upgrade-Insecure-Requests": "1"
        },
        "jxzxehall": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Upgrade-Insecure-Requests": "1"
        },
        "library": {
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest"
        }
    }
}