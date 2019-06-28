from bs4 import BeautifulSoup
import requests
from w3lib.html import remove_tags
from tika import parser
import os

def get_schools(soup):
    selector = "h3 > a"
    school_pages = soup.select(selector)
    schools = [remove_tags(str(school)) for school in school_pages]
    res = []
    for tag in school_pages:
        res.append(tag['href'])
    return res

def get_school_data(base,school_page,status):
    # Parse out all a tags to get pdfs
    # Get pdf data (might need separate functino)
    activity_page = requests.get(base+school_page)
    soup = BeautifulSoup(activity_page.text, 'html.parser')
    school_name_selector = soup.select("h1", class_="heading--title")
    if school_name_selector:
        school_name = school_name_selector[0].text
    else:
        print ("Error: school name not found. Skipping school: {}".format(school_page))
        return
    if not os.path.exists('schools/'+status+'/'+school_name): # Make a directory for the school if it doesn't already exist
        try:
            desired_permission = int('077',8)
            original_umask = os.umask(0)
            os.makedirs('schools/'+status+'/'+school_name)
        except:
            print ("Error: permission denied to create directories.")
        finally:
            os.umask(original_umask)
    pdf_links = soup.find_all("a", class_="publication-link")
    for link in pdf_links:
        pdf = link['href']
        report_name = link['href'].split('/')[-1]
        # doc_link = requests.get(base+link)
        path = 'schools/'+status+'/'+school_name+'/'+report_name
        # with open(path+'.pdf', 'wb') as f: # Download report pdf
        #     f.write(doc_link.content)
        # f.close()
        try:
            raw = parser.from_file(pdf)
            with open(path+'.txt', 'w') as txt_file:
                txt_file.write(raw['content'])
            txt_file.close()
        except:
            print ("Error: Tika could not parse file")

def get_next_page(soup):
    next_page = [tag for tag in soup.find_all('a') if tag.get("class") == "pagination__next"]
    next_page = soup.find_all('a', {'class': 'pagination__next'})
    if next_page:
        return next_page[0]['href']

def main():
    open = "/search?q=&location=&radius=3&status%5B0%5D=1&start=42500&rows=10"
    # closed = "/search?q=&location=&radius=&radius=3&latest_report_date_start=&latest_report_date_end=&status%5B%5D=2"
    # urls = [open, closed]
    closed = "/search?q=&location=&radius=3&status%5B0%5D=2&start=52000&rows=10"
    urls = [open]
    base = "https://reports.ofsted.gov.uk"
    if not os.path.exists("schools"):
        try:
            desired_permission = int('0777',8)
            original_umask = os.umask(0)
            os.makedirs('schools', desired_permission)
            os.makedirs('schools/open', desired_permission)
            os.makedirs('schools/closed', desired_permission)
        except:
            print ("Error: permission denied to create directories.")
            print ("You can avoid this error by creating a schools directory in the root of this project with subdirectories schools/open and schools/closed")
        finally:
            os.umask(original_umask)
    count = 1
    for url in urls:
        next = True
        while next:
            page = requests.get(base+url)
            soup = BeautifulSoup(page.text, 'html.parser')
            if soup.find_all("h1")[0].text == "Slim Application Error":
                continue # retry the url in case an application error occurs
            schools = get_schools(soup)
            for school in schools:
                if count == 0:
                    get_school_data(base,school,"open")
                else:
                    get_school_data(base,school,"closed")
            next_page = get_next_page(soup)
            if next_page:
                url = next_page
            else:
                next = False
                count += 1

main()
