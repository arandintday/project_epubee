import os
import time
import random
import urllib
import requests
import sys
import shutil
import zipfile
from xml.dom.minidom import parse
from bs4 import BeautifulSoup as bs
import xml.dom.minidom as xdm
print("Please input epubee link, exit to quit:")
print("Example:http://reader.obook.vip/books/mobile/62/6244a56007d3b59ac79d0e870b455b6e/")
cache_path="/sdcard/Download/cache"
book_path="/sdcard/Download/book"
while True:
    book_link=input()
    if "reader.obook.vip/books/mobile" in book_link:
        break
    elif "exit" in book_link:
        sys.exit()
    else:
        print("[-] E:Invailed link, please check your link and retry!")
isCacheExists=os.path.exists(cache_path)
if isCacheExists:
    shutil.rmtree(cache_path)#清除旧文件夹
    print("[*] Cache cleared successfully")
    os.makedirs(cache_path)#建立新文件夹
else:
    os.makedirs(cache_path)
isBookExists=os.path.exists(book_path)
if not isBookExists:
    os.makedirs(book_path)
opf_link=book_link+"content.opf"
for i in range(1,11):
    try:
        urllib.request.urlretrieve(opf_link,"{}/content.opf".format(cache_path))
        break
    except Exception as e:
        print("[-] E:{}".format(e))
        print("[-] Retrying {} of 10 times".format(i))
        time.sleep(random.randint(1,4))
isOpfExists=os.path.exists(cache_path+"/content.opf")
if isOpfExists:
    print("[+] Opf file download successfully")
else:
    print("[-] Opf file download failed, please check your internet connection!")
    sys.exit()
xml_doom=xdm.parse("{}/content.opf".format(cache_path))
book_info=xml_doom.documentElement
book_name=book_info.getElementsByTagName("dc:title")
#print(book_name[0].childNodes[0].data)
name=book_name[0].childNodes[0].data
book_author=book_info.getElementsByTagName("dc:creator")
#print(book_author[0].childNodes[0].data)
author=book_author[0].childNodes[0].data
book_content=book_info.getElementsByTagName("item")
max_num=len(book_content)
num=1
print("[*] Opf file analyze successfully")
print("[*] Downloading contents...")
for b_item in book_content:
    #print(b_item.getAttribute("href"))
    for j in range(1,50):
        try:
            item=b_item.getAttribute("href")
            if "/" in item:
                sub_link=item.split("/")
                sub_path="{}/{}".format(cache_path,sub_link[0])
                isSubExists=os.path.exists(sub_path)
                if not isSubExists:
                    os.makedirs(sub_path)
                urllib.request.urlretrieve("{}{}".format(book_link,item),"{}/{}".format(sub_path,sub_link[1]))
            elif "html" in item:
                #urllib.request.urlretrieve("{}{}".format(book_link,item),"{}//{}".format(cache_path,item))
                r=requests.get("{}{}".format(book_link,item),timeout=5)
                soup=bs(r.content,"html5lib")
                try:
                    soup.find('div',class_="readertop").decompose()
                    soup.find('div',class_="readermenu").decompose()
                    soup.find('div',class_="reader-to-vip c-pointer").decompose()
                except:
                    print("[*] Nothing to remove")
                f=open("{}/{}".format(cache_path,item),'w',encoding='utf-8')
                f.write(str(soup))
                f.close()
            else:
                urllib.request.urlretrieve("{}{}".format(book_link,item),"{}/{}".format(cache_path,item))
            break
        except Exception as e:
            print("[-] E:{}".format(e))
            print("[-] Retrying {} of 50 times".format(j))
            time.sleep(random.randint(1,4))
    print("[*] {} of {} items downloaded".format(num,max_num),end="\r")
    num+=1
print("[+] Content download successfully")
f=open("{}/mimetype".format(cache_path),'w',encoding='utf-8')
f.write("application/epub+zip")
f.close()
print("[*] Mimetype file create successfully")
os.makedirs("{}/META-INF".format(cache_path))
f=open("{}/META-INF/container.xml".format(cache_path),'w',encoding='utf-8')
f.write('<?xml version="1.0"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n   <rootfiles>\n      <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>\n   </rootfiles>\n</container>')
f.close()
print("[*] Meta info create successfully")
new_book=zipfile.ZipFile("{}/tmp.zip".format(book_path),'w')
print("[*] Packaging...")
pack=os.walk(cache_path)
for current_path,subfolders,filesname in pack:
    for file in filesname:
        src=os.path.join(current_path,file)
        dst=src.replace(cache_path,"",1)
        #print("{},{}".format(src,dst))
        new_book.write(src,arcname=dst,compress_type=zipfile.ZIP_STORED)
new_book.close()
os.rename("{}/tmp.zip".format(book_path),"{}/{}-{}.epub".format(book_path,name,author))
print("[*] {}-{} download successfully".format(name,author))
