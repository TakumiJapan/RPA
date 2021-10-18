import os
import pandas as pd
from selenium.webdriver.chrome.options import Options
import selenium.webdriver as webdriver
import time
from email.message import EmailMessage
import smtplib
from conf import query, num_page, receiver, my_login, my_password

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
         "download.prompt_for_download": False,
         "download.directory_upgrade": True,
         "plugins.always_open_pdf_externally": True}
chrome_options.add_experimental_option('prefs', prefs)
os.environ["webdriver.chrome.driver"] = webdriver_path   # 'webdriver' executable needs to be in PATH. Please see https://sites.google.com/a/chromium.org/chromedriver/home

links_list = [query_link + str(page+1) for page in range(num_page)]   # create links to follow

driver = webdriver.Chrome(executable_path=webdriver_path, chrome_options=chrome_options)

final_info = []   # empty dictionary for articles info
for search_link in links_list:
    # get all links to articles from the page
    driver.get(search_link)
    time.sleep(5)
    articles = driver.find_elements_by_xpath("//a[@data-selenium-selector='title-link']")

    articles_links = []
    for article in articles:
        try:
            link = article.get_attribute("href")
            articles_links.append(link)
        except:
            pass

    for link in articles_links:
        # get info of each article
        tmp_info = {}

        driver.get(link)
        text = driver.find_elements_by_xpath("//*[@data-selenium-selector='paper-detail-page-header']")[0].text

        tmp_info.update({
                        'title': text.split("\n")[1],
                        'year': text.split("\n")[3].split(" ")[1],   # TODO: might convert to datetime
                        'authors': text.split("\n")[2],
                        'journal': text.split("\n")[5],
                        'abstract': text.split("\n")[6],
                        })

        citation = driver.find_elements_by_xpath("//*[@data-selenium-selector='scorecard-citation-intent']")[0].text

        tmp_info.update({
            'Number of citations': citation.split("\n")[0].split(" ")[0]})

        # trying to download the article's doc
        try:
            initial_dir = os.listdir(folder_for_pdf)
            driver.find_element_by_xpath("//*[@data-selenium-selector='paper-link']").click()
            time.sleep(5)

            current_dir = os.listdir(folder_for_pdf)
            filename = list(set(current_dir) - set(initial_dir))[0]
            full_path = os.path.join(folder_for_pdf, filename)

        except Exception as e:
            full_path = None

        tmp_info.update({'path_to_file': full_path})

        final_info.append(tmp_info.copy())
        time.sleep(2)

driver.quit()

# write all info to excel
df = pd.DataFrame(final_info)
excel_path = os.path.join(working_dir, "data.xlsx")
df.to_excel(excel_path, index=False)

# create email
login, password = my_login, my_password   # could be setup manually
mail = EmailMessage()
mail['From'] = login
mail['To'] = receiver
mail['Subject'] = "Topics analysis"
mail.set_content("Hi!\n\nFind attached excel file with articles info.\n\nRegard,\nKerber Ekaterina ")

# add attachment
with open(excel_path, 'rb') as f:
    file_data = f.read()
    file_name = f'articles_info.xlsx'
mail.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

# send email
server = smtplib.SMTP('smtp.office365.com')
server.starttls()
server.login(login, password)
server.send_message(mail)
server.quit()
