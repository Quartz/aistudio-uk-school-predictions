import requests
from bs4 import BeautifulSoup

open_start = "/search?start=10&status%5B0%5D=1&rows=10"
close_start = "/search?q=&location=&radius=3&status%5B0%5D=2&start=10&rows=10"
base = "https://reports.ofsted.gov.uk"

def get_next_page(soup):
    next_page = [tag for tag in soup.find_all('a') if tag.get("class") == "pagination__next"]
    next_page = soup.find_all('a', {'class': 'pagination__next'})
    if next_page:
        return next_page[0]['href']

def get_urls(url,res,base):
    next = True
    while next:
        page = requests.get(base+url)
        print(base+url)
        soup = BeautifulSoup(page.text, 'html.parser')
        if soup.find_all("h1")[0].text == "Slim Application Error":
            continue
        res.append(url)
        next_page = get_next_page(soup)
        if next_page:
            url = next_page
        else:
            next = False
    return res

open_urls = get_urls(open_start,[],base)
closed_urls = get_urls(close_start,[],base)

with open('open_urls.txt','w') as open_txt:
    for url in open_urls:
        open_txt.write(url+'\n')
open_txt.close()

with open('closed_urls.txt','w') as closed_txt:
    for url in closed_urls:
        closed_txt.write(url+'\n')
closed_txt.close()
