import os
import pandas as pd
from selenium.webdriver.chrome.options import Options
import selenium.webdriver as webdriver
import time
from email.message import EmailMessage
import smtplib
from conf import query, num_page, receiver
from datetime import datetime

query_link = f"https://www.semanticscholar.org/search?q={query}&sort=relevance&page="

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
os.environ["webdriver.chrome.driver"] = webdriver_path   # 'webdriver' executable needs to be in PATH.

links_list = [query_link + str(page+1) for page in range(num_page)]  # create links to follow

driver = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options)

final_list = []   

for search_link in links_list:
    # get all links to articles from the page
    count = 0 #number of articles on the page
    driver.get(search_link)
    time.sleep(5)

    articles = driver.find_elements_by_xpath("//*[@data-selenium-selector='title-link']")
    publication_links = []
    

    for article in articles:
        try:
            link = article.get_attribute("href")
            publication_links.append(link)

        except:
            pass
    #body > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(4) > div:nth-child(1) > ul:nth-child(1) > li:nth-child(1) > div:nth-child(1) > a:nth-child(1) > div:nth-child(1)        
    citation_count = []
    citations = driver.find_elements_by_xpath("//h4[@class='dropdown-filters__result-count__header']")
    for citation in citations:
        try:
            citation_count.append(citation.text)

        except:
            pass

    publication_dates = []
    temp_dates = driver.find_elements_by_class_name('cl-paper-pubdates')
    count +=1
    for data in temp_dates:
        try:
            publication_dates.append(data.text)

        except:
            pass
        

    for link in publication_links:
        # get info of each article 
        tmp_info = {}

        driver.get(link)
        
        paper_detail_title = driver.find_elements_by_xpath("//*[@data-selenium-selector='paper-detail-title']")[0].text
        paper_meta_item = driver.find_elements_by_class_name('paper-meta-item')[0].text
        citing_papers = driver.find_elements_by_xpath("//a[@data-heap-nav='citing-papers']")[0].text,
        tmp_info.update({
                        'title': paper_detail_title,
                        'authors': paper_meta_item,
                        'date' : publication_dates[count],
                        'citation': citing_papers
                        })

        # trying to download the article's doc

        try:
            initial_dir = os.listdir(folder_for_pdf)
            #driver.find_element_by_xpath("//*[@id='download']").click()
            driver.find_element_by_xpath("//*[@class='alternate-sources__dropdown-wrapper']").click()
            time.sleep(5)

            current_dir = os.listdir(folder_for_pdf)

            filename = list(set(current_dir) - set(initial_dir))[0] #eliminate duplicates
            full_path = os.path.join(folder_for_pdf, filename)

        except Exception as e:
            full_path = None

        tmp_info.update({'path_to_file':full_path})

        final_list.append(tmp_info.copy())
        time.sleep(2)
        
driver.quit()


# write all info to excel
df = pd.DataFrame(final_list)
excel_path = os.path.join(working_dir, "data.xlsx")
df.to_excel(excel_path, index=False)

# create email
login, password = "", ""
mail = EmailMessage()
mail['From'] = login
mail['To'] = receiver
mail['Subject'] = "Topics analysis"
mail.set_content("Hi!\n\nFind attached excel file with articles info.\n\nRegard,")

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
