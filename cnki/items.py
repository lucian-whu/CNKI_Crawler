# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class CnkiItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # primary fileds
    title = Field()
    authors_list = Field()
    orgs_list = Field()
    abstract = Field()
    kws_list = Field()
    cat_num = Field()
    ref = Field()

    # Housekepping fileds
    url = Field()
