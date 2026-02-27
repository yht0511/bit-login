import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import time
import functools
from fastapi.middleware.cors import CORSMiddleware
import re

# Import bit-login components
from bit_login.service import jwb_login, jxzxehall_login
from bit_login.services.jwb import jwb
from bit_login.services.jxzxehall import jxzxehall
from bit_login.login import login_error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("bit_login_server")

app = FastAPI(
    title="BIT Login Services API",
    description="High concurrency RESTful API for BIT services",
    version="1.0.0"
)

# 允许的域名列表
ALLOWED_ORIGINS = [
    "https://bit101.cn",
    "http://bit101.cn",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,       # 基础白名单
    allow_origin_regex=r'^https?://[a-zA-Z0-9\-]+\.bit101\.cn$',  # 子域名通配
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class BaseCredentials(BaseModel):
    username: str
    password: str

class JwbScoreRequest(BaseCredentials):
    kksj: Optional[str] = None
    detailed: bool = False

class JwbAllScoreRequest(BaseCredentials):
    detailed: bool = False

class JxzxehallCoursesRequest(BaseCredentials):
    kksj: Optional[str] = None

# --- Session Management ---

class SessionManager:
    def __init__(self):
        self._cache = {}  # (username, service_name): (session, timestamp)
        self._ttl = 1800  # 30 minutes (Session timeout)

    def get_session(self, username, service_name):
        key = (username, service_name)
        if key in self._cache:
            session, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return session
            else:
                del self._cache[key]
        return None

    def set_session(self, username, service_name, session):
        key = (username, service_name)
        self._cache[key] = (session, time.time())

    def invalidate(self, username, service_name):
        key = (username, service_name)
        if key in self._cache:
            del self._cache[key]

session_manager = SessionManager()

def get_service_session(login_cls, username, password, service_name):
    """Get session from cache or login."""
    # Try cache
    session = session_manager.get_session(username, service_name)
    if session:
        return session
    
    # Login
    logger.info(f"Performing fresh login for {username} - {service_name}")
    try:
        service_login = login_cls()
        service_login.login(username, password)
        session = service_login.get_session()
        session_manager.set_session(username, service_name, session)
        return session
    except login_error as e:
        logger.warning(f"Login failed for user {username}: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Login failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during login for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error during login: {str(e)}")

def execute_service(login_cls, service_cls, username, password, service_name, func_name, **kwargs):
    """
    Execute a service function with auto-retry mechanism.
    
    Args:
        login_cls: The login class (e.g., jwb_login)
        service_cls: The service wrapper class (e.g., jwb)
        username: User's username
        password: User's password
        service_name: Unique name for session caching (e.g., 'jwb')
        func_name: Name of the method to call on service_cls instance
        **kwargs: Arguments for the service method
    """
    
    # Function to create service instance and call method
    def call_service(s):
        srv = service_cls(s)
        method = getattr(srv, func_name)
        return method(**kwargs)

    session = get_service_session(login_cls, username, password, service_name)
    
    try:
        # Attempt 1
        return call_service(session)
    except Exception as e:
        logger.info(f"First attempt failed for {username} on {service_name}.{func_name}. Reason: {str(e)}")
        
        # Invalidate cache and retry with fresh login
        session_manager.invalidate(username, service_name)
        session = get_service_session(login_cls, username, password, service_name)
        
        try:
            # Attempt 2
            return call_service(session)
        except Exception as final_e:
            logger.error(f"Second attempt failed for {username} on {service_name}.{func_name}. Reason: {str(final_e)}")
            raise HTTPException(status_code=500, detail=f"Service execution failed: {str(final_e)}")

# --- Endpoints ---

@app.get("/")
async def root():
    return {"message": "BIT Login Services API is running"}

# --- JWB Services ---

@app.post("/api/jwb/score", summary="Get scores for a specific semester")
def get_jwb_score(request: JwbScoreRequest):
    """
    Get scores from JWB system.
    """
    result = execute_service(
        jwb_login, jwb, 
        request.username, request.password, 'jwb', 
        'get_score', 
        kksj=request.kksj, detailed=request.detailed
    )
    return {"data": result}

@app.post("/api/jwb/all_score", summary="Get all scores")
def get_jwb_all_score(request: JwbAllScoreRequest):
    """
    Get all scores from JWB system.
    """
    result = execute_service(
        jwb_login, jwb, 
        request.username, request.password, 'jwb', 
        'get_all_score', 
        detailed=request.detailed
    )
    return {"data": result}

# --- JXZXEHALL Services ---

@app.post("/api/jxzxehall/student_data", summary="Get student personal data")
def get_student_data(request: BaseCredentials):
    """
    Get student personal information from JXZXEHALL.
    """
    result = execute_service(
        jxzxehall_login, jxzxehall, 
        request.username, request.password, 'jxzxehall', 
        'get_student_data'
    )
    return {"data": result}

@app.post("/api/jxzxehall/credit", summary="Get student credit info")
def get_credit(request: BaseCredentials):
    """
    Get student credit information.
    """
    result = execute_service(
        jxzxehall_login, jxzxehall, 
        request.username, request.password, 'jxzxehall', 
        'get_credit'
    )
    return {"data": result}

@app.post("/api/jxzxehall/courses", summary="Get courses")
def get_courses(request: JxzxehallCoursesRequest):
    """
    Get student courses (schedule).
    """
    result = execute_service(
        jxzxehall_login, jxzxehall, 
        request.username, request.password, 'jxzxehall', 
        'get_courses', 
        kksj=request.kksj
    )
    return {"data": result}

@app.post("/api/jwb/cookies", summary="Get JWB login cookies")
def get_jwb_cookies(request: BaseCredentials):
    """
    Get raw cookies after logging into JWB system and return formatted strings.
    """
    session = get_service_session(
        jwb_login, 
        request.username, 
        request.password, 
        'jwb'
    )
    
    try:
        cookies_dict = session.cookies.get_dict()
        cookie_list = [f"{k}={v};" for k, v in cookies_dict.items()]
        cookie_str = "\n".join(cookie_list)+" Path=/; Domain=webvpn.bit.edu.cn; HttpOnly"
        
        return {
            "data": cookies_dict,
            "cookie_str": cookie_str,
            "cookie_list": cookie_list
        }
    except Exception as e:
        logger.error(f"Failed to extract cookies for JWB: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to extract cookies from session")


@app.post("/api/jxzxehall/cookies", summary="Get JXZXEHALL login cookies")
def get_jxzxehall_cookies(request: BaseCredentials):
    """
    Get raw cookies after logging into JXZXEHALL (教学中心) system and return formatted strings.
    """
    session = get_service_session(
        jxzxehall_login, 
        request.username, 
        request.password, 
        'jxzxehall'
    )
    
    try:
        cookies_dict = session.cookies.get_dict()
        cookie_list = [f"{k}={v};" for k, v in cookies_dict.items()]
        cookie_str = "\n".join(cookie_list)+" Path=/; Domain=webvpn.bit.edu.cn; HttpOnly"

        return {
            "data": cookies_dict,
            "cookie_str": cookie_str,
            "cookie_list": cookie_list
        }
    except Exception as e:
        logger.error(f"Failed to extract cookies for JXZXEHALL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to extract cookies from session")

if __name__ == "__main__":
    # For local testing
    uvicorn.run("server:app", host="0.0.0.0", port=16384, reload=True)
