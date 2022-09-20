from bs4 import BeautifulSoup
import requests
import csv

CSV = 'cards.csv'
site = 'https://proaim.ru'
base = 'https://proaim.ru/catalog/operatorskaya_tekhnika/'


def get_html(url,params=''):
    r = requests.get(url,params=params)


def get_content(html):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find_all('div', class_='catalog_item main_item_wrapper item_wrap')

    cards = []
    for item in items:
        cards.append(
            {
                'title':item.find('div',class_='item-title').getText(strip=True),
                'http': site + item.find('a',class_='dark_link').get('href'),
                'price':item.find('span', class_='price_value').getText(),
                'img': site + item.find('div', class_='image_wrapper_block').find('img').get('src'),
            }
        )
    return cards

def csv_save(items,path):
    with open(path,'w',newline='') as file:
        writer = csv.writer(file,delimiter=';')
        writer.writerow(['Название','Ссылка','Цена','Картинка'])
        for item in items:
            writer.writerow([item['title'],item['http'],item['price'],item['img'], ])


def parser():
    PAGINATION = int(input('Укажите число страниц: '))
    html = get_html(base)
    if html.status_code == 200:
        cards = []
        for page in range(1,PAGINATION):
            print(f'Пасим страницу {page}')
            html = get_html(base,params={'page':page})
            cards.extend(get_content(html.text))
            csv_save(cards, CSV)
    else:
        print('error')

parser()
if __name__ == '__main__':
    get_content()