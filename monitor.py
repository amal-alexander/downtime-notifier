import requests

def check_url_status(url):
    try:
        r = requests.get(url, timeout=10)
        return r.status_code == 200
    except:
        return False