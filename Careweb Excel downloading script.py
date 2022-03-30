#!/usr/bin/env python
# coding: utf-8

# In[ ]:


########################READ_ME########################
# This script uses for downloading excel files from careweb Benchmarks and Data https://careweb.careguidelines.com/benchmarks/
# Before running the script, please make sure these libraries are installed on your python editor:
# requests
# selenium
# webdriver_manager
# ChromeDriverManager
# BeautifulSoup
#
# When running the script, it opens up chrome web site and connect to the target careweb site. Websites will be closed after
# downloading is complete. Please don't close the browser manually.
# Since the website requires users to log in, users have to pass in the MCG username and password before running the script.
# There are 4 parameters need to pass in in the end of the script (if __name__ == '__main__' section): 
# username, password, editionnum and saveaspath
# editionnum uses for identity edition version of excel files, default is set to 26, please pass in number only (e.x. 26)
# saveaspath is for users to point the local folder that for all excel files to be saved in, please pass in double slashs
# (e.x. 'C:\\temp')
#The script creates a folder in the saveaspath users specified, named as Benchmarks_and_Data_editionnumber_Date, all excel files
#will be saved in this folder.
# please reach out to Cheng Gao if have any questions: chengxi.gao@mcg.com
#######################################################

from datetime import date
import time
import os
import requests
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class FileDownloading(object):
    
    def __init__(self,username, password, editionnum = 26, saveaspath = 'C:\\temp'): #Default edition num sets to 26, local path sets to 'C:\\temp' 
            for num in re.findall(r'\d+', str(editionnum)):#take digits from editionnum
                editionnum = num
            self.editionnum = editionnum
            self.saveaspath = saveaspath.replace('\t', '\\t')
            self.dest_folder =saveaspath+ "\\Benchmarks_and_Data_" + str(editionnum) + 'th_' + str(date.today())
            self.username = username
            self.password = password
        
    def createfolders(self):
        if not os.path.exists(self.dest_folder):
            os.makedirs(self.dest_folder)  # create folder if it does not exist
            print("Folders have been created in "+self.dest_folder)
        else:
            print("Folders already exists in "+self.dest_folder)
            

    def get_file_urls(self):
        links_set = set()
        urls_list = []
        
        #log in to webcare 
        requests_session = requests.Session()
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get("https://login.mcg.com/account/login?returnUrl=https%3A%2F%2Fcgi.careguidelines.com%2F&ClientId=Careweb") 


        username = driver.find_element_by_id("Email")
        password = driver.find_element_by_id("Password")

        username.send_keys(self.username)
        password.send_keys(self.password)

        driver.find_element_by_class_name("log-btn").click()
        
        #Save cookie to use requests for getting page elements
        for cookie in driver.get_cookies():
            requests_session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

        driver.quit()
        
        #Start to use requests
        resp = requests_session.get('https://careweb.careguidelines.com/scripts/benchmarks_toc.pl')
        resp.encoding = resp.apparent_encoding

        data = BeautifulSoup(resp.text, 'html')

        for tag in data.find_all("li"):
            #print(tag.text)
            for link in tag.findAll('a'):
                if '/ed%s/'%self.editionnum in link.get('href'): 
                     links_set.add(link.get('href'))
        
        #Save target webpage url to links_list
        links_list = list(map(lambda link : 'https://careweb.careguidelines.com'+link, links_set ))
        
        def flatten(t):
            return [item for sublist in t for item in sublist]
        
        #Flatten the list for urls
        for web in links_list:
            files_list=[]
            resp = requests_session.get(web)
            resp.encoding = resp.apparent_encoding
            data = BeautifulSoup(resp.text, 'html')

            for link in data.findAll('a'):
                files_list.append(link.get('href'))

            left_text = web.split('/')[-1]
            web = web.replace(left_text,'')

            filtered_files_list = list(filter(None, files_list))
            final_url = list(map(lambda link : web+link, filtered_files_list ))
            final_url_no_htm = list(filter(lambda k: '.htm' not in k, final_url))
            urls_list.append(final_url_no_htm)

        final_url_list = flatten(urls_list)
        
        #Remove duplicated urls and return the set
        print("url list generation is complete!")
        return(set(final_url_list))

    def downloading(self): #Function for downloading the Excel files from urls
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : self.dest_folder} #Set download folder to our destination folder
        chromeOptions.add_experimental_option("prefs",prefs)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chromeOptions)
        
        #Use Selenium to log in to careweb page
        driver.get("https://login.mcg.com/account/login?returnUrl=https%3A%2F%2Fcgi.careguidelines.com%2F&ClientId=Careweb") 
        username = driver.find_element_by_id("Email")
        password = driver.find_element_by_id("Password")

        username.send_keys(self.username)
        password.send_keys(self.password)
        
        driver.find_element_by_class_name("log-btn").click()
        
        #Start to download Excels
        try:
            for url in self.get_file_urls():
                driver.get(url)
                time.sleep(5)
        except:
            print("Downloading went wrong!")
        
        #After all downloads start, wait for 30s before closing the web broswer
        time.sleep(30)
        print("Downloading is complete!")
        driver.quit()
        
if __name__ == '__main__':
    #Example:
#     downloadExcel = FileDownloading(
#         username = 'chengxi.gao@mcg.com', 
#         password = 'xxxxxxxxxxxx',
#         editionnum = 26,
#         # Remember to use \\ instead of \ in saveaspath
#         saveaspath = 'C:\\Users\\cgao\\Downloads\\test_folder')
    
    downloadExcel = FileDownloading(
        username = 'xxxxxxxxxxxxxx', 
        password = 'xxxxxxxxxxxxxx',
        editionnum = 25, 
        saveaspath = 'C:\\Users\\cgao\\Downloads\\test_folder')
    
    downloadExcel.createfolders()
    downloadExcel.downloading()


# In[ ]:




