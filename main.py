import json
import time

from bs4 import BeautifulSoup
import datetime
import csv
import aiohttp
import asyncio

start_time = time.time()
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9 ",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 "
                  "Safari/537.36",
}
books_data = []


async def get_page_data(session, page):
    url = f'https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table&page={page}'

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')

        books_item = soup.find('tbody', class_="products-table__body").find_all('tr')

        for book in books_item:
            book_data = book.find_all('td')

            # catch title
            try:
                book_title = book_data[0].find('a').text
            except:
                book_title = 'Нет названия'

            # catch author
            try:
                book_author = book_data[1].find('a').text
            except:
                book_author = 'Нет автора'

            # catch publisher
            try:
                book_publisher = book_data[2].find('a').text
            except:
                book_publisher = 'Нет издателя'

            # catch price
            try:
                book_price = int(book_data[3].find('span').find('span').text.strip().replace(' ', ''))
            except:
                book_price = 'Цена неизвестна'

            books_data.append(
                {
                    'book_title': book_title,
                    'book_author': book_author,
                    'book_publisher': book_publisher,
                    'book_price': book_price,
                }
            )
        print(f'INFO: страница {page}')


async def gather_data():
    url = 'https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), 'lxml')
        pages_count = int(soup.find('div', class_='pagination-number').find_all('a')[-1].text)

        tasks = []
        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)
        await asyncio.gather(*tasks)


def main():
    asyncio.run(gather_data())
    current_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')

    with open(f'labirint_{current_time}.json', 'w') as file:
        json.dump(books_data, file, indent=4, ensure_ascii=False)

    with open(f'labirint_{current_time}.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Название книги',
                'Автор',
                'Издательство',
                'Цена'
            )
        )

    for book in books_data:
        with open(f'labirint_{current_time}.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    book['book_title'],
                    book['book_author'],
                    book['book_publisher'],
                    book['book_price'],
                )
            )

    finish_time = time.time() - start_time
    print(f'Затраченное время: {finish_time}')


if __name__ == '__main__':
    main()
