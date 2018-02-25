# coding=utf-8
import urllib
import urllib2
import re
import sys
import os
import requests
from pyquery import PyQuery as Pq


class PicSpider(object):

    def __init__(self, searchText):
        self.url = "http://www.baidu.com/baidu?wd=%s&tn=monline_4_dg" % searchText
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 Safari/600.5.17"}
        self._page = None
        reload(sys)
        sys.setdefaultencoding('utf8') 

    def baiduSearch(self):
        if not self._page:
            r = requests.get(self.url, headers=self.headers)
            self._page = Pq(r.text)
        return [site.attr('href') for site in self._page('div.result.c-container  h3.t  a').items()]

    def getUrls(self):
        tmpUrls = self.baiduSearch()
        self.siteUrls = []
        for tmpUrl in tmpUrls:
            tmpPage = requests.get(tmpUrl, allow_redirects=False)
            if tmpPage.status_code == 200:
                urlMatch = re.search(r'URL=\'(.*?)\'', tmpPage.text.encode('utf-8'), re.S)
                self.siteUrls.append(urlMatch.group(1))
            elif tmpPage.status_code == 302:
                self.siteUrls.append(tmpPage.headers.get('location'))
            else:
                print('An invalid url in search result.')
 
    def getContents(self,siteUrl):
        response = requests.get(siteUrl, headers=self.headers)
        response.encoding = 'utf-8'
        pattern = re.compile(r'<img src="(.*?)"',re.S)
        items = re.findall(pattern,response.text)
        contents = []
        for item in items:
            contents.append(item)
        return contents

    def saveImgs(self,images,name):
        number = 1
        print u"发现",name,u"共有",len(images),u"张图片"
        for imageURL in images:
            splitPath = imageURL.split('.')
            fileName = name + "/" + str(number) + "." + splitPath[-1]
            self.saveImg(imageURL,fileName)
            number += 1
 
    def saveImg(self,imageUrl,fileName):
        if re.match(r'^https?:/{2}\w.+$', imageUrl):
            req = urllib2.Request(imageUrl)  
            req.add_header("User-Agent",self.headers["User-Agent"])
            req.add_header("Referer", imageUrl)
            try:
                u = urllib2.urlopen(req)
            except:
                return
            data = u.read()
            f = open(fileName, 'wb')
            f.write(data)
            f.close()
            print(imageUrl+' ok.')            
 
    def mkdir(self,path):
        isExists=os.path.exists(path)
        if not isExists:
            print u"为\"",path,u"\"新建文件夹："
            os.makedirs(path)

    def getPics(self):
        self.getUrls()
        for siteUrl in self.siteUrls:
            print(siteUrl+":")
            contents = self.getContents(siteUrl)
            self.mkdir(siteUrl.strip()[8:-1])
            self.saveImgs(contents,siteUrl.strip()[8:-1])
        sys.setdefaultencoding('ascii')


s=PicSpider("")
s.getPics()
