# -*- coding: utf-8 -*-
#!/usr/bin/python3

__author__ = 'beimenchuixue'
__blog__ = 'http://www.cnblogs.com/2bjiujiu/'

import pymysql
import requests


class RandomIp(object):
    headers = {
        'Referer': 'http://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCDB',
    }

    def __init__(self):
        # 初始化连接配置和连接参数
        db_settings = {
            'host': 'localhost',
            'db': 'ipProxy',
            'user': 'bryan',
            'password': 'password',
            'charset': 'utf8',
            'use_unicode': True
        }

        # self.db_setting = crawler.settings.get('db_setting')
        self.conn = pymysql.connect(**db_settings)
        self.cursor = self.conn.cursor()

    # # 获取配置文件中db_settings
    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler)

    def get_random_ip(self):
        """获取有效的ip地址"""
        # 建立索引映射
        ip_index, port_index, ip_type_index = 0, 1, 2
        # sql查询语句,随机获取一行值
        sql = 'select ip, port, ip_type from ip_server order by rand() limit 1'
        try:
            # 从数据库中获取一行值
            self.cursor.execute(sql)
            # 对于查询结果不能直接获取，需要通过fetchall，索引来取每个值
            for info in self.cursor.fetchall():
                # print(info)
                ip = info[ip_index]
                port = info[port_index]
                ip_type = info[ip_type_index]
                effective_ip = self.check_ip(ip, port, ip_type)
                if effective_ip:
                    return effective_ip
                else:
                    self.del_usedless_ip(ip)
                    return self.get_random_ip()
            # print('*******************' + str(type(ip_type)) +
            #       '*********************************\n')
            # print('*******************' + str(ip_type) +
            #       '*********************************\n')
            # print(ip)
            # print(port)
        except Exception as e:
            print(e)

    def check_ip(self, ip, port, ip_type):
        """检查这个ip是否有效"""
        http_url = 'https://www.baidu.com'
        proxy_url = '{ip_type}://{ip}:{port}'.format(
            ip_type=ip_type.lower(), ip=ip, port=port)
        try:
            prox_dict = {
                'http': proxy_url
            }
            response = requests.get(
                http_url, proxies=prox_dict, headers=self.headers)
        except Exception as e:
            print(e)
            return False
        else:
            if 200 <= response.status_code <= 300:
                return proxy_url
            else:
                self.del_usedless_ip(ip)
                return False
        pass

    def del_usedless_ip(self, ip):
        """删除无效的ip"""
        sql = 'delete from ip_server where ip=%s' % ip
        self.cursor.execute(sql)
        self.conn.commit()


# if __name__ == '__main__':
#     # 测试
#     ip = RandomIp()
#     effective_ip = ip.get_random_ip()
#     print(effective_ip)
#     pass
