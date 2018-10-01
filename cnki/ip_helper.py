# -*- coding: utf-8 -*-
#!/home/bryan/anaconda3/bin/python3

__author__ = 'beimenchuixue'
__blog__ = 'http://www.cnblogs.com/2bjiujiu/'

import requests
import pymysql
from time import sleep
from random import randint, choice
from scrapy.selector import Selector
from twisted.enterprise import adbapi
from twisted.internet import reactor

# 数据库基本配置, 自行配置
db_settings = {
    'host': 'localhost',
    'db': 'ipProxy',
    'user': 'bryan',
    'password': 'password',
    'charset': 'utf8',
    'use_unicode': True
}
# conn = pymysql.connect(**db_settings)
# cursor = conn.cursor()

# 生成连接池
db_conn = adbapi.ConnectionPool('pymysql', **db_settings)


def go_sleep():
    """进行随机io堵塞，模仿人访问"""
    while randint(0, 1):
        sleep(choice([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]))


def get_sql(ip, port, ip_type):
    """获得sql语句"""
    if ip and port and ip_type:
        sql = """insert into
              ip_server(ip, port, ip_type)
               value (%s, %s, %s)
              on DUPLICATE key update ip=values(ip), port=values(port), ip_type=values(ip_type)"""
        try:
            params = (ip, int(port), ip_type)
        except Exception as e:
            print(e)
            return None
        return sql, params
    else:
        return None


def go_insert(cursor, sql, params):
    """数据库插入操作"""
    try:
        cursor.execute(sql, params)
    except Exception as e:
        print(e)


def get_ip():
    """爬取ip信息并存入数据库"""
    # 设置请求头
    headers = {
        'Referer': 'http://www.xicidaili.com/nn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    # 获取5页的数据
    for page in range(1, 50):
        # 建立关系映射，增加程序可阅读性
        ip_index, port_index, type_index = 2, 3, 6
        # 爬取的url
        url = 'http://www.xicidaili.com/nn/{page}'.format(page=page)

        go_sleep()

        response = requests.get(url, headers=headers)
        # 打印状态码
        print(response.status_code)
        # 进行页面解析
        selectors = Selector(text=response.text)
        all_trs = selectors.css('#ip_list .odd')
        for tr in all_trs:
            ip = tr.css('td:nth-child(%s)::text' % ip_index).extract_first()
            port = tr.css('td:nth-child(%s)::text' %
                          port_index).extract_first()
            ip_type = tr.css('td:nth-child(%s)::text' %
                             type_index).extract_first()
            sql, params = get_sql(ip, port, ip_type)
            if sql:
                try:
                    # cursor.execute(sql, params)
                    # conn.commit()
                    # 执行sql操作
                    db_conn.runInteraction(go_insert, sql, params)

                except Exception as e:
                    print(e)
            else:
                break


if __name__ == '__main__':
    get_ip()
    # 让twisted的sql操作去完成
    reactor.callLater(4, reactor.stop)
    reactor.run()