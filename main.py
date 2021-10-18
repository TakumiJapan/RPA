import os
import pandas as pd
from selenium.webdriver.chrome.options import Options
import selenium.webdriver as webdriver
import time
from conf import query, num_page

query_link = f"https://www.semanticscholar.org/search?q={query}&page="

# working paths
working_dir = os.path.dirname(os.path.realpath(__file__))
folder_for_pdf = os.path.join(working_dir, "articles")
webdriver_path = os.path.join(working_dir, "chromedriver")

# chek if articles directory is exist and create if not
if not os.path.isdir(folder_for_pdf):
    os.mkdir(folder_for_pdf)

# webdriver
chrome_options = Options()
prefs = {"download.default_directory": folder_for_pdf,
         "download.prompt_for_download": False}
chrome_options.add_experimental_option('prefs', prefs)
os.environ["webdriver.chrome.driver"] = webdriver_path  # 'webdriver' executable needs to be in PATH.

links_list = [query_link + str(page + 1) for page in range(num_page)]  # create links to follow
driver = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options)

final_list = []

for search_link in links_list:
    count = 0
    driver.get(search_link)
    time.sleep(5)

    articles = driver.find_elements_by_xpath("//*[@data-selenium-selector='title-link']")
    print(articles)
    publications = []

    for article in articles:
        try:
            link = article.get_attribute("href")
            publications.append(link)

        except Exception as e:
            print(e)
            pass

    pubdates = []
    temp_dates = driver.find_elements_by_class_name('cl-paper-pubdates')
    count += 1
    for data in temp_dates:
        try:
            pubdates.append(data.text)
        except Exception as e:
            print(e)
            pass

    for link in publications:
        tmp_info = {}
        driver.get(link)

        paper_detail_title = driver.find_elements_by_xpath("//*[@data-selenium-selector='paper-detail-title']")[0].text
        paper_authors = driver.find_elements_by_class_name('paper-meta-item')[0].text
        cit_source = driver.find_elements_by_xpath("//a[@data-heap-nav='citing-papers']")
        if len(cit_source) != 0:
            cit_papers = cit_source[0].text
        else:
            cit_papers = 'No citing papers'

        tmp_info.update({
            'title': paper_detail_title,
            'authors': paper_authors,
            'date': pubdates[count],
            'citation': cit_papers
        })

        # trying to download the article's doc

        try:
            initial_dir = os.listdir(folder_for_pdf)
            driver.find_element_by_xpath("//*[@class='alternate-sources__dropdown-wrapper']").click()
            time.sleep(5)
            current_dir = os.listdir(folder_for_pdf)
            filename = list(set(current_dir) - set(initial_dir))[0]
            full_path = os.path.join(folder_for_pdf, filename)

        except Exception as e:
            print(e)
            full_path = None

        tmp_info.update({'path_to_file': full_path})

        final_list.append(tmp_info.copy())
        time.sleep(2)

driver.quit()

# write all info to excel
df = pd.DataFrame(final_list)
excel_path = os.path.join(working_dir, "data.xlsx")
df.to_excel(excel_path, index=False)
