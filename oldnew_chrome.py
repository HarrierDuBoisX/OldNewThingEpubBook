from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from database import Database

from PIL import Image
from io import BytesIO
import os
import w3lib.url




class Chrome:
  def __init__(self):
    self.options = Options()
    self.options.add_argument("--headless=new")
    self.options.add_argument("--incognito")
    self.options.add_argument("--window-size=1920x1080")
    self.options.add_argument("--start-maximized")
    self.options.add_argument("--disable-gpu")  # Last I checked this was necessary.
    self.options.add_argument("--disable-dev-shm-usage")
    self.options.add_argument("--no-sandbox")  # Bypass OS security model
    self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    current_path = os.getcwd()+"\\OldNewThings"
    self.options.binary_location = current_path + "\\chrome\\chrome.exe"
    self.chrome_driver = current_path + "\\chromedriver.exe"
    #self.chrome_driver = current_path + "\\driver"
    self.service = Service(executable_path=self.chrome_driver)
    #self.service = Service()
    self.driver = webdriver.Chrome(options=self.options, service=self.service)

  def __del__(self):
    self.driver.quit()

  def get_url(self, url):
    self.driver.get(url)

  def get_screenshoot(self, filename):
    self.driver.get_screenshot_as_file(filename)


class Crawler:
  def __init__(self, url, databasename = 'site_db.db'):
    self.pages = set()
    self.visited = set()
    self.post_title = str()
    self.post_date = str()
    self.post = str()
    self.post_html = str()
    self.tags = str()
    self.db = Database(databasename)
    self.brows = Chrome()
    self.base_url = url

  def __del__(self):
    self.db.close()
  
  def return_clean_url(self, url):
    newurl = url
    sharp_position = url.rfind('#')
    if(sharp_position != -1):
        newurl = url[:-(len(url)-sharp_position)]
    return newurl;
    
  def crawl (self, url):
    try:
      url = w3lib.url.url_query_cleaner(url, ('p',)) 
      self.brows.get_url(url)
      self.visited.add(url)
      if(url.find(self.base_url) != -1):
        self.grab_page(url)
      try:
        elems = self.brows.driver.find_elements(By.XPATH,"//a[@href]")
        for elem in elems:
          t_url = elem.get_attribute("href").lower()
          if(t_url.rfind('#') != -1):
            t_url = w3lib.url.url_query_cleaner(t_url, ('p',)) 
          if(t_url.startswith("https://devblogs.microsoft.com/oldnewthing/") and t_url.find("redirect_to") == -1 and t_url.find("redirect") == -1 and t_url.find("base64") == -1 and t_url.find("login") == -1):
            self.pages.add(t_url)
      except Exception as e:
          print('Href Error:')
          print(type(e))    
          print(e.args)     
          print(e)                  
      self.pages -= self.visited
    except Exception as e:
      print(type(e))    
      print(e.args)     
      print(e)                



  def grab (self):
    self.crawl(self.base_url)
    while len(self.pages) > 0:
      self.crawl(next(iter(self.pages)))

  def grab_page (self, url):
    try:
      temp = self.brows.driver.find_elements(By.XPATH, '//*[@id="featured"]')
      if(len(temp) > 0):
        try:
          self.tags = self.brows.driver.find_element(By.XPATH, '/html/body/div[3]/main/div[2]/div/div/div/article/footer/span').text
        except Exception as e:
          print('Tag Error:')
          print(type(e))    
          print(e.args)     
          print(e)          
        for element in temp:
          self.post_title = element.find_element(By.CSS_SELECTOR, '.entry-title').text
          self.post_date = element.find_element(By.CSS_SELECTOR, '.entry-meta > p:nth-child(1)').text
          self.post = element.text
          self.post_html = element.get_attribute("outerHTML")
#          print(element.text)
#          print(element.tag_name)
#          print(element.get_attribute("class"))
        self.db.cursor.execute ('''INSERT INTO Blog
                            (url, title, date, post, post_html, tags)
                            VALUES(:url,:title,:date,:post,:post_html,:tags)''',
                            {'url':url, 'title':self.post_title, 'date':self.post_date, 'post':self.post, 'post_html':self.post_html, 'tags':self.tags}
                            )
        self.db.conn.commit()
    except Exception as e:
      print(type(e))    
      print(e.args)     
      print(e)          





try:
  b = Crawler(url='https://devblogs.microsoft.com/oldnewthing/', databasename='oldnewthing.db')
  b.grab()
  b.brows.get_screenshoot('capture.png')


except Exception as e:
  print('Exception: ')
  print(type(e))    # the exception instance
  print(e.args)     # arguments stored in .args
  print(e)          # __str__ allows args to be printed directly,
  # Roll back any change if something goes wrong
  #raise e

finally:
  print('finally: ')





# $x('//*[@id="featured"]')
# $$('html.js body.post-template-default.single.single-post.postid-109155.single-format-standard.custom-background.wp-featherlight-captions div#page.hfeed.site main#main.site-main div#single-wrapper.wrapper div#content.container div#mainContent.row div#primary.col-md.content-area article#post-109155.addtoanyshare div#featured.row.justify-content-center.postcontent.remove_dcss')
