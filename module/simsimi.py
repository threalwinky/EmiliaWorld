from module.lib import *

def get_simsimi_response(message):
    headers = {
        'Content-Type':'application/x-www-form-urlencoded',
    }
    API_ENDPOINT = 'https://api.simsimi.vn/v1/simtalk'
    data = {
        'text' : message,
        'lc' : 'vn',
        'key' : ''
    }
    res = requests.post(url = API_ENDPOINT, headers=headers, data=data)
    json_text = json.loads(res.text)
    return json_text['message']