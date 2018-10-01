# -*- coding: utf-8 -*-
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy

from scrapy.loader.processors import MapCompose
from scrapy.loader import ItemLoader
from cnki.items import CnkiItem
import re
from scrapy.http import Request
from bs4 import BeautifulSoup
from scrapy_splash import SplashRequest


class CnkiSpider(scrapy.Spider):
    name = 'cnki'
    start_urls = [
        'http://nvsm.cnki.net/kns/brief/result.aspx?dbprefix=SCDB&crossDbcodes=CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CJRF,CJFN,CCJD']
    # start_urls = [
    #     'http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CFJD&dbname=CJFDTEMN&filename=ZJCA201819002&v',
    #     'http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CJFQ&dbname=CJFDTEMP&filename=GJGZ201804003&v',
    #     'http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CFJD&dbname=CJFDTEMN&filename=JXKS201837005&v',
    #     'http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CJFQ&dbname=CJFDTEMP&filename=KSYJ201809003&v']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, args={'images': 0, 'timeout': 3})

    def parse(self, response):
        print(response.text)
        article_url = response.xpath(
            '//*[@id="ctl00"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/a/@href').extract()[0]
        article_req = Request(url=article_url, callback=self.parseArticle)
        yield article_req

    def parseArticle(self, response):
        loader = ItemLoader(item=CnkiItem(), response=response)
        loader.add_xpath(
            'title', '//*[@id="mainArea"]/div[3]/div[1]/h2/text()', MapCompose(unicode.strip, unicode.title))
        loader.add_xpath('authors_list', '//*[@id="mainArea"]/div[3]/div[1]/div[1]//a/text()',
                         MapCompose(MapCompose(unicode.strip, unicode.title)))
        loader.add_xpath(
            'orgs_list', '//*[@id="mainArea"]/div[3]/div[1]/div[2]//a/text()', MapCompose(unicode.strip, unicode.title))
        loader.add_xpath(
            'abstract', '//*[@id="ChDivSummary"]/text()', MapCompose(unicode.strip, unicode.title))
        loader.add_xpath('kws_list', '//*[@id="catalog_KEYWORD"]/..//a/text()', MapCompose(
            unicode.strip, unicode.title, lambda i: i.strip(';')))
        loader.add_xpath(
            'cat_num', '//*[@id="catalog_ZTCLS"]/../text()', MapCompose(
                unicode.strip, unicode.title, lambda i: i.strip(';')))
        # loader.add_xpath(
        #     'ref', '/html/body/div[1]/ul/li[1]/a[1]', MapCompose(
        #         unicode.strip, unicode.title, lambda i: i.strip(';')))

        # Housekeeping fields
        loader.add_value('url', response.url)
        filename = re.search(r'(?<=filename=).*?(?=&v)', response.url).group()
        citation_url = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CFJD&filename=' + \
            filename.lower() + '&dbname=CJFDTEMN&RefType=1&vl='
        citation_req = Request(url=citation_url, callback=self.parseCitation)
        citation_req.meta['item'] = loader.load_item()
        yield citation_req

    def parseCitation(self, response):
        item = response.meta['item']
        refs_line = ''
        soup = BeautifulSoup(response.text, 'lxml')
        refs_list = soup.find_all('li')
        for i in range(1, len(refs_list) + 1):
            ref = refs_list[i - 1]
            try:
                title = ref.find(
                    'a', {'target': 'kcmstarget'}).getText().strip()
                authors = re.sub(r"[A-Za-z0-9\!\%\[\]\,\\。\.\s]", '',
                                 ref.find('a', {'target': 'kcmstarget'}).next_sibling)
                orgs = ref.find('a').find_next().get_text()
                date = ref.find('a').find_next().next_sibling
                refs_line = refs_line + '\n' + str(i) + '.' + authors + '.' + \
                    title + '.' + orgs + '.' + date + \
                    '.(11)'  # pesudo issue month
            except AttributeError:
                try:
                    info_list = re.sub(
                        r"[A-Za-z\!\%\[\]\,\\。\.\s]+", ',', ref.find('em').next_sibling).split(',')
                    title = info_list[0]
                    orgs = info_list[1]
                    authors = info_list[2][:-1]
                    date = info_list[3]
                    refs_line = refs_line + '\n' + str(i) + '.' + authors + '.' + \
                        title + '.' + orgs + '.' + date + \
                        '.(11)'  # pesudo issue month
                except IndexError:
                    refs_line = ''
        item['ref'] = refs_line
        return item
