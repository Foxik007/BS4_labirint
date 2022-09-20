
import csv
import json
import time

import requests
from bs4 import BeautifulSoup
import lxml
import asyncio
import aiohttp

books_data = []
start_time = time.time()


async def get_page_data(session, page):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
    }

    url = f"https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table&page={page}"

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, "lxml")

        books_items = soup.find("tbody", class_="products-table__body").find_all("tr")

        for bi in books_items:
            book_data = bi.find_all("td")

            try:
                book_title = book_data[0].find('a').text.strip()
            except:
                book_title = 'Нет названия книги'

            try:
                book_author = book_data[1].text.strip()
            except:
                book_author = 'Нет автора'

            try:
                book_publ = book_data[2].find_all('a')
                book_publ = ':'.join(bp.text for bp in book_publ)
            except:
                book_publ = 'Нет издательства'

            try:
                book_new_price = int(book_data[3].find('div', class_='price').find('span').find('span').text.strip().replace(' ', ''))
            except:
                book_new_price = 'Нет цены'

            try:
                book_old_price = int(book_data[3].find('span', class_='price-gray').text.strip().replace(' ', ''))
            except:
                book_old_price = 'Нет старой цены'

            try:
                book_sale = round(((book_old_price - book_new_price) / book_old_price) * 100)
            except:
                book_sale = 'Скидки нет'

            try:
                in_stock = book_data[-1].text.strip()
            except:
                in_stock = 'Нет в наличии'

            books_data.append({
                'Название': book_title,
                'Автор': book_author,
                'Издательство': book_publ,
                'Цена со скидкой': book_new_price,
                'Цена без скидки': book_old_price,
                'Наличие': in_stock,
                '% скидки': book_sale,
            })
        print(f'Обработано {page}')

async def gather_data():
    url = f'https://www.labirint.ru/genres/2308/?display=table'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url)
        soup = BeautifulSoup(await response.text(),'lxml')
        pages_count = int(soup.find('div', class_='pagination-numbers').find_all('a')[-1].text)

        tasks = []

        for page in range(1,pages_count + 1):
            task = asyncio.create_task(get_page_data(session,page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.get_event_loop().run_until_complete(gather_data())

    with open("labyrinth_async.json", "w") as file:
        json.dump(books_data, file, indent=4, ensure_ascii=False)

    with open("labyrinth_async.csv", "w") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "book_title",
                "Автор",
                "Издательство",
                "Цена со скидкой",
                "Цена без скидки",
                "Процент скидки",
                "Наличие на складе"
            )
        )

    for book in books_data:
        with open("labyrinth_async.csv", "a") as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    book["Название"],
                    book["Автор"],
                    book["Издательство"],
                    book["Цена со скидкой"],
                    book["Цена без скидки"],
                    book["Наличие"],
                    book["% скидки"]
                )
            )


if __name__ == '__main__':
    main()



#start_time = time.time()
#def get_data():
#    with open('labirint.csv','w') as f:
#        writer = csv.writer(f)
#        writer.writerow(
#            (
#                'Название',
#                'Автор',
#                'Издание',
#                'Новая цена',
#                'Старая цена',
#                'Наличие',
#                '% скидки',
#
#            )
#        )
#
#
#    url = f'https://www.labirint.ru/genres/2308/?display=table'
#
#    r = requests.get(url=url)
#    soup = BeautifulSoup(r.content,'lxml')
#
#    pages_count = int(soup.find('div',class_='pagination-numbers').find_all('a')[-1].text)
#    books_data = []
#
#    for page in range(1,pages_count + 1):
#        url = f'https://www.labirint.ru/genres/2308/?display=table&page={page}'
#
#        response = requests.get(url)
#
#        soup = BeautifulSoup(response.content,'lxml')
#
#        books_items = soup.find('tbody',class_='products-table__body').find_all('tr')
#
#        for bi in books_items:
#            book_data = bi.find_all('td')
#
#            try:
#                book_title = book_data[0].find('a').text.strip()
#            except:
#                book_title = 'Нет названия книги'
#
#            try:
#                book_author = book_data[1].text.strip()
#            except:
#                book_author = 'Нет автора'
#
#            try:
#                book_publ = book_data[2].find_all('a')
#                book_publ = ':'.join(bp.text for bp in book_publ)
#            except:
#                book_publ = 'Нет издательства'
#
#            try:
#                book_new_price = int(book_data[3].find('div',class_='price').find('span').find('span').text.strip().replace(' ',''))
#            except:
#                book_new_price = 'Нет цены'
#
#            try:
#                book_old_price = int(book_data[3].find('span',class_='price-gray').text.strip().replace(' ',''))
#            except:
#                book_old_price = 'Нет старой цены'
#
#            try:
#                book_sale = round(((book_old_price - book_new_price) / book_old_price )* 100)
#            except:
#                book_sale = 'Скидки нет'
#
#            try:
#                in_stock = book_data[-1].text.strip()
#            except:
#                in_stock = 'Нет в наличии'
#
#
#            books_data.append  ({
#                'Название':book_title,
#                'Автор':book_author,
#                'Издание':book_publ,
#                'Новая цена':book_new_price,
#                'Старая цена':book_old_price,
#                'Наличие':in_stock,
#                '% скидки':book_sale
#            })
#
#            with open('labirint.csv', 'a') as f:
#                writer = csv.writer(f)
#                writer.writerow(
#                    (
#                        book_title,
#                        book_author,
#                        book_publ,
#                        book_new_price,
#                        book_old_price,
#                        in_stock,
#                        book_sale,
#
#                    )
#                )
#
#        print(f'Обработано {page} из {pages_count}')
#        time.sleep(1)
#
#
#    with open('lab.json', 'w', encoding='utf-8') as f:
#        json.dump(books_data,f,indent=4,ensure_ascii=False)
#
#
#def main():
#    get_data()
#    finish_time = time.time() - start_time
#    print(finish_time)
#
#
#if __name__ == '__main__':
#    main()