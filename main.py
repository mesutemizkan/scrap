import requests, time
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials

base_url = "https://365canvas.com"

categories = [
    "black-and-white",
    "song-lyric",
    "map",
    "collage",
    "family",
    "couple",
    "dog",
    "wedding",
    "anniversary",
    "motivational",
    "memorial"
]


def post_on_sheets(data, category):

    SERVICE_ACCOUNT_FILE = 'sheets_service_account.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    gc = gspread.authorize(credentials)
    sh = gc.open('365')
    worksheet = sh.worksheet(category)
    worksheet.append_row(data)


def get_category_products(category):

    url = base_url + '/t/' + category + "-canvas-prints"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    main_container = soup.find(class_="module mod-list-product pb-15 pt-8 md:py-12 relative")
    all_link_items = main_container.find_all("a")

    page_count = 1

    try:
        page_count = len(main_container.find_all("option"))

        for page in range (2, page_count + 1):
            page_url = base_url + '/t/' + category + "-canvas-prints" + f"/page/{page}/"

            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            main_container = soup.find(class_="module mod-list-product pb-15 pt-8 md:py-12 relative")
            all_link_items.extend(main_container.find_all("a"))

    except Exception as e:
        print(f"Error occured while getting page count: {e}")

    print("\n\n")
    print(f"Procesing category: {url} | Total product: {len(all_link_items)} | Total page: {page_count}")


    for link_item in all_link_items:
        try:
            product_link = link_item.get('href')

            print(f"Processing product: {product_link}")

            response = requests.get(product_link)
            soup = BeautifulSoup(response.text, 'html.parser')

            sheet_data = [product_link]

            try:
                title = soup.find(class_='product_title entry-title text-base font-senmibold text-secondary-900 md:text-h3-xl').text.strip()
                sheet_data.append(title)
            except Exception as e:
                print(f"Error occured in title: {e}", product_link)

            try:
                description = soup.find(class_='inside-toggle-content last-mb-none').text.strip()
                sheet_data.append(description)
            except Exception as e:
                print(f"Error occured in descripton: {e}", product_link)

            try:
                image = soup.find(class_='img-pro-large bg bg-center relative').get("data-href")
                sheet_data.append(image)
            except Exception as e:
                print(f"Error occured in image: {e}", product_link)

            post_on_sheets(sheet_data, category)
            time.sleep(2)

        except Exception as e:
            print("Error occured in product link request", link_item.get('href'), e)
            continue


if __name__ == '__main__':

    # c = 'song-lyric'
    # get_category_products(c)

    for c in categories:
        get_category_products(c)

