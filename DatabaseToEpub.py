
import os
from database import Database
from ebooklib import epub
from bs4 import BeautifulSoup



def get_last_id(url):
  id = 0
  sharp_position = url.rfind('?')
  if(sharp_position != -1):
    id = url[-(len(url)-sharp_position):]
    newstr = ''.join((ch if ch in '0123456789.-e' else ' ') for ch in id)
    lon = [int(i) for i in newstr.split()]
    return lon
  return id

def remove_tag(soup, tag, nclass):
  tmp = soup.find_all(tag, class_=nclass) 
  for op in tmp:
    op.decompose()
  return soup

book = epub.EpubBook()

current_path = os.getcwd()+"\\OldNewThings\\Finals"
dbpath = current_path + '\\oldnewthing.db'
db = Database(dbpath)
#db.cursor.execute('SELECT * FROM Blog WHERE id BETWEEN 6900 AND 7000;')
db.cursor.execute('SELECT * FROM Blog;')

rows = db.cursor.fetchall()

rows.sort(key=lambda a: get_last_id(a[1]))


book.set_identifier('id_TheOLdNewThingBlogSBook')
book.set_title('The Old New Thing Blog sBook')
book.set_language('en')

book.add_author('Raymond Chen')
book.add_author('Selenium', file_as='scraping all blog posts', role='ill', uid='coauthor')

# add cover image
book.set_cover("cover.jpg", open('cover.jpg', 'rb').read())


contents = []
for index, row in enumerate(rows):
  text = row[5]
  soup = BeautifulSoup(text, 'html.parser')
  to_rem = remove_tag(soup, "div", "post-detail-avatar")
  to_rem = remove_tag(to_rem, "div", "entry-meta entry-meta-layout")
  to_rem = remove_tag(to_rem, "div", "postdetail-author-info")
  text = to_rem.prettify()
  c = epub.EpubHtml(uid=f"chapter{index+1}", title=row[2], file_name=f"post_{index + 1}.xhtml", lang='en', media_type="application/xhtml+xml")
  c.set_content(text)
  contents.append(c) 
    
for c1 in contents:
  book.add_item(c1)



#allLink = [epub.Link(cont.file_name, cont.title, cont.id) for cont in contents]
#tupleLink = [(link, cont.title) for link, cont in  zip(allLink, contents)]
# define Table Of Contents
'''book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),
            (
              epub.Section('Languages1'),
              (c1, c2),
            ),
            (
              epub.Section('Languages2'),
              (c_list[3], ),
            ),
            (
              epub.Section('Languages3'),
              (
                (
                  epub.Section('Languages4'),
                  (c_list[4], c_list[5]),
                ),
              ),
            ),
            )'''
#book.toc = ((epub.Section('posts'), contents), )
#toc = [(epub.Section('Posts'), contents)]
#book.toc = toc
book.toc = (epub.Link('cover.xhtml', 'Intro', 'intro'),
              (
                epub.Section('Posts'), 
                (contents), 
              ), )


# create spin, add cover page as first page
book.spine = ['cover','nav'] + contents

# define CSS style
style = '''
@namespace epub "http://www.idpf.org/2007/ops";

body {font-family: "Segoe UI Web Regular","Segoe UI Regular WestEuropean","Segoe UI",Tahoma,Arial,Roboto,"Helvetica Neue",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";}

'''

nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

# add CSS file
book.add_item(nav_css)
# add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())


# write to the file
epub.write_epub("TheOldNewThing.epub", book, {})
