import datetime
import random
import requests
import time
import json


AppId = ''
AppSecret = ''
AccessTokenUrl = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'

users = dict(
    zhiyuanchen=dict(
        name='Zhiyuan Chen',
        openid='',
        products=['max']
    )
)

TemplateId = ''
TemplateUrl = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'

products = dict(
    normal=dict(
        name='iPhone 12',
        stocks='https://reserve-prime.apple.com/CN/zh_CN/reserve/G/availability.json',
        stores='https://reserve-prime.apple.com/CN/zh_CN/reserve/F/stores.json',
        purchase='https://reserve-prime.apple.com/CN/zh_CN/reserve/F/availability'
    ),
    pro=dict(
        name='iPhone 12 Pro',
        stocks='https://reserve-prime.apple.com/CN/zh_CN/reserve/A/availability.json',
        stores='https://reserve-prime.apple.com/CN/zh_CN/reserve/A/stores.json',
        purchase='https://reserve-prime.apple.com/CN/zh_CN/reserve/A/availability'
    ),
    mini=dict(
        name='iPhone 12 mini',
        stocks='https://reserve-prime.apple.com/CN/zh_CN/reserve/H/availability.json',
        stores='https://reserve-prime.apple.com/CN/zh_CN/reserve/H/stores.json',
        purchase='https://reserve-prime.apple.com/CN/zh_CN/reserve/H/availability'
    ),
    max=dict(
        name='iPhone 12 Pro Max',
        stocks='https://reserve-prime.apple.com/CN/zh_CN/reserve/G/availability.json',
        stores='https://reserve-prime.apple.com/CN/zh_CN/reserve/G/stores.json',
        purchase='https://reserve-prime.apple.com/CN/zh_CN/reserve/G/availability'
    )
)

beijing = dict(
    R320='三里屯',
    R479='华贸购物中心',
    R645='朝阳大悦城',
    R448='王府井',
    R388='西单大悦城'
)

models = {
    'MGC73CH/A': '蓝色 256GiB',
    'MGC63CH/A': '金色 256GiB',
    'MGC43CH/A': '黑色 256GiB',
}


def get(request, to_json=True):
    while True:
        try:
            response = requests.get(request)
            content = response.text
            if to_json:
                content = json.loads(content)
        except ConnectionError:
            print(f'ERROR:\tFailed to establish connection')
            print(request)
            print()
        except json.decoder.JSONDecodeError:
            print(f'ERROR:\tResponse could not be decoded')
            print(response.text)
            print()
        else:
            break
    return content


def post(request, data=''):
    while True:
        try:
            response = requests.post(request, data)
            content = response.text
        except ConnectionError:
            print(f'ERROR:\tFailed to establish connection')
            print(request)
            print()
        except json.decoder.JSONDecodeError:
            print(f'ERROR:\tResponse could not be decoded')
            print(response.text)
            print()
        else:
            break
    return content


def query(product='max', stores=beijing):
    try:
        content = get(products[product]['stocks'])
    except KeyError:
        raise ValueError(f'Invalid product {product} specified')
    stocks = dict()
    for store in stores.keys():
        stock = [models[model] for model in models.keys() if True in content['stores'][store][model]['availability'].values()]
        if stock:
            stocks[store] = stock
    return stocks, content


def get_access_token(appId=AppId, appSecret=AppSecret, accessTokenUrl=AccessTokenUrl):
    content = get(AccessTokenUrl.format(appId, appSecret))
    access_token = content['access_token']
    access_token_expiry = time.time() + content['expires_in']
    return access_token, access_token_expiry


def notify(user, access_token, product, stocks, stores=beijing, templateId=TemplateId, templateUrl=TemplateUrl):
    request = templateUrl.format(access_token)

    value1 = products[product]['name']
    value2 = users[user]['name']
    value3 = str(datetime.datetime.today())
    value4 = ''
    value5 = ''

    for index, (store, stock) in enumerate(stocks.items()):
        if index == 0:
            value5 = f'{stores[store]}: {", ".join(stock)}'
        elif index == 1:
            value4 = f'{stores[store]}: {", ".join(stock)}'
        elif index == 2:
            value3 = f'{stores[store]}: {", ".join(stock)}'
        elif index == 3:
            value2 = f'{stores[store]}: {", ".join(stock)}'
        elif index == 4:
            value1 = f'{stores[store]}: {", ".join(stock)}'

    data = dict(
        touser=users[user]['openid'],
        template_id=templateId,
        url=products[product]['purchase'],
        data=dict(
            first=dict(
                value='感谢您使用zyc.ai提供的内容',
                color='#173177'
            ),
            keyword1=dict(
                value=value1,
                color='#173177'
            ),
            keyword2=dict(
                value=value2,
                color='#173177'
            ),
            keyword3=dict(
                value=value3,
                color='#173177'
            ),
            keyword4=dict(
                value=value4,
                color='#173177'
            ),
            keyword5=dict(
                value=value5,
                color='#173177'
            ),
            remark=dict(
                value='Developed by ZhiyuanChen\nAll rights reserved',
            )
        )
    )
    response = post(request, json.dumps(data))
    print(f'Sent notifications to {user}')
    return response


def run():
    print('Monitoring starts now')
    begin = datetime.time(5, 59, 0)
    end = datetime.time(6, 2, 0)
    token, expiry = get_access_token()
    force_sleep = False
    while True:
        if expiry - time.time() < 120:
            token, expiry = get_access_token()
        for name, info in users.items():
            for product in info['products']:
                stocks, content = query(product)
                if stocks:
                    notify(name, token, product, stocks)
                    force_sleep = True
                with open('log', 'a+') as f:
                    f.writelines(json.dumps(content))
        now = datetime.datetime.now().time()
        if force_sleep or now < begin or now > end:
            sleep_time = random.randint(0, 2000000000) / 100000000
            if force_sleep:
                sleep_time *= 30
            time.sleep(sleep_time)
            reason = 'force_sleep' if force_sleep else 'general'
            print(f'Sleeping for {sleep_time}s by {reason}')


def test():
    print('Monitoring starts now')
    begin = datetime.time(5, 59, 0)
    end = datetime.time(6, 2, 0)
    token, expiry = get_access_token()
    while True:
        if expiry - time.time() < 120:
            token, expiry = get_access_token()
        for name, info in users.items():
            for product in info['products']:
                stocks, content = query(product)
                notify(name, token, product, stocks)
                print(content)
        now = datetime.datetime.now().time()
        if not (now > begin and now < end):
            sleep_time = random.randint(0, 2000000000) / 10000000
            time.sleep(sleep_time)
            print(f'Sleeping for {sleep_time}s')


if __name__ == '__main__':
    print('Thanks for using zyc.ai contents')
    print('Please crarefully read the End User License Aggrement')
    print('at https://zyc.ai/about/eula')
    run()
