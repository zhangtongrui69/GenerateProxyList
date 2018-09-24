from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import urllib
import time
import threading
import queue
import random
# from bs4 import BeautifulSoup
import socket
from struct import *
import pymysql
import requests

# import bs4
# import codecs

# target_url="http://www.google.com/"  # visit this website while verify the proxy
# target_string='Google Search'		# the returned html text should contain this string
target_url = "http://www.baidu.com/"  # visit this website while verify the proxy
target_string = '030173'		# the returned html text should contain this string
target_timeout = 30                   # the response time should be less than target_timeout seconds
                                    # then we consider this is a valid proxy


dbpassword='tme'
# items in q is a list: ip, port, protocol, country
q = queue.Queue()
qout = queue.Queue()

def generateProxyListFromGatherProxy():
    driver = webdriver.Chrome()
    driver.get('http: // www.gatherproxy.com /')
#    driver.get('http://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0')
    while True:
        t = driver.find_element_by_class_name('DataGrid')
        trs = t.find_elements_by_tag_name('tr')
        for tr in trs:
            tds = tr.find_elements_by_tag_name('td')
            ip = ''
            port = 0
            protocol=''
            if len(tds)==10:
                for idx, td in enumerate(tds):
                    if idx == 0:
                        lk = td.find_element_by_tag_name('a')
                        if 'IP' in lk.text:
                            break
                        ip = lk.text
                    elif idx == 1:
                        port = int(td.text)
                    elif idx == 2:
                        if td.text == 'HTTPS':
                            protocol = 'https'
                        elif td.text == 'HTTP':
                            protocol = 'http'
                        elif 'SOCKS' in td.text:
                            protocol= 'socks'
                    elif idx==4:
                        country = td.text
                        a = (ip, port, protocol, country)
                        q.put(a)
                        break
                    else:
                        pass
        anchors = driver.find_elements_by_tag_name('a')
        nextPage=None
        bNext = False
        for anchor in anchors:
            if '下一页' in anchor.text or 'Next' in anchor.text:
                nextPage = anchor
                bNext = True
                break
        if bNext:
            nextPage.click()
        else:
            break
    driver.quit()
    return

def generateProxyListFromProxynova():
    driver = webdriver.Chrome()
    driver.get('http://www.proxynova.com/proxy-server-list/')

    trs = driver.find_elements_by_tag_name('tr')
    for tr in trs:
        tds = tr.find_elements_by_tag_name('td')
        ip = ''
        port = 0
        protocol = 'http'
        country=''
        for idx, td in enumerate(tds):
            if idx == 0:
                if (len(td.text) > 0):
                    ip = td.text
                else:
                    break
            elif idx == 1:
                port = int(td.text)
            elif idx==5:
                anchor = td.find_element_by_tag_name('a')
                country = anchor.text
                a = (ip, port, protocol, country)
                q.put(a)
            else:
                pass
    driver.quit()
    return


def generateProxyListFromFreeproxylists():
    driver = webdriver.Chrome()
    driver.get('http://www.freeproxylists.net')
#    driver.get('http://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0')
    while True:
        t = driver.find_element_by_class_name('DataGrid')
        trs = t.find_elements_by_tag_name('tr')
        for tr in trs:
            tds = tr.find_elements_by_tag_name('td')
            ip = ''
            port = 0
            protocol=''
            if len(tds)==10:
                for idx, td in enumerate(tds):
                    if idx == 0:
                        lk = td.find_element_by_tag_name('a')
                        if 'IP' in lk.text:
                            break
                        ip = lk.text
                    elif idx == 1:
                        port = int(td.text)
                    elif idx == 2:
                        if td.text == 'HTTPS':
                            protocol = 'https'
                        elif td.text == 'HTTP':
                            protocol = 'http'
                        elif 'SOCKS' in td.text:
                            protocol= 'socks'
                    elif idx==4:
                        country = td.text
                        a = (ip, port, protocol, country)
                        q.put(a)
                        break
                    else:
                        pass
        anchors = driver.find_elements_by_tag_name('a')
        nextPage=None
        bNext = False
        for anchor in anchors:
            if '下一页' in anchor.text or 'Next' in anchor.text:
                nextPage = anchor
                bNext = True
                break
        if bNext:
            nextPage.click()
        else:
            break
    driver.quit()
    return


def generateProxyListFromFree_proxy_lists():
    driver = webdriver.Chrome()
    driver.get('http://free-proxy-list.net/')
    next = driver.find_element_by_id('proxylisttable_next')
    nexta = next.find_element_by_tag_name('a')

    lastPage = False
    while True:
        t = driver.find_element_by_id('proxylisttable')
        if not t:
            driver.quit()
            return
        tb = t.find_element_by_tag_name('tbody')
        trs = tb.find_elements_by_tag_name('tr')
        for tr in trs:
            tds = tr.find_elements_by_tag_name('td')
            ip = ''
            port = 0
            country = ''
            a = tuple()
            if len(tds)==8:
                for idx, td in enumerate(tds):
                    if idx == 0:
                        if td.text == 'IP地址':
                            break
                        ip = td.text
                    elif idx == 1:
                        port = int(td.text)
                    elif idx == 2:
                        country = td.text
                    elif idx == 6:
                        if td.text == 'yes':
                            a = (ip, port, 'https', country)
                        else:
                            a = (ip, port, 'http', country)
                        q.put(a)
        if lastPage:
            break
#        actions = ActionChains(driver)
#        actions.move_to_element(nexta).perform()
        driver.execute_script("arguments[0].scrollIntoView();", nexta)
        driver.execute_script("scrollBy(0,-100)")
        nexta.click()
        next = driver.find_element_by_id('proxylisttable_next')
        nexta = next.find_element_by_tag_name('a')
        next_class = next.get_attribute('class')
        if 'disabled' in next_class:
            lastPage = True
    driver.quit()
    return


def generateProxyListFromSocks_proxy_net():
    driver = webdriver.Chrome()
    driver.get('http://www.socks-proxy.net/')

    while True:
        next = driver.find_element_by_id('proxylisttable_next')
        nexta = next.find_element_by_tag_name('a')
        next_class = next.get_attribute('class')
        t = driver.find_element_by_id('proxylisttable')
        if not t:
            driver.quit()
            return
        tb = t.find_element_by_tag_name('tbody')
        trs = tb.find_elements_by_tag_name('tr')
        for tr in trs:
            tds = tr.find_elements_by_tag_name('td')
            ip = ''
            port = 0
            country = ''
            if len(tds)==8:
                for idx, td in enumerate(tds):
                    if idx == 0:
                        if td.text == 'IP地址':
                            break
                        ip = td.text
                    elif idx == 1:
                        port = int(td.text)
                    elif idx==3:
                        country = td.text
                    elif idx == 4:
                        if 'Socks' in td.text:
                            a = (ip, port, td.text, country)
                            q.put(a)
                            break
                        else:
                            break
        if 'disabled' in next_class:
            break
        nexta.click()
    driver.quit()
    return


def generateProxyListFromNordVpn():
    driver = webdriver.Chrome()
    driver.get('https://nordvpn.com/free-proxy-list/')
    time.sleep(3)
    try:
        dlg = driver.find_element_by_class_name('modal-content')
        if dlg:
            close = dlg.find_element_by_class_name('Popup__close')
            if close:
                close.click()
                time.sleep(1)
    except:
        pass
    for i in range(5):
        loadmores = driver.find_elements_by_class_name('btn-brand-yellow')
        for loadmore in loadmores:
            if loadmore.text == 'Load more':
                break
        loadmore.click()
        time.sleep(1)
    time.sleep(2)
    t = driver.find_element_by_class_name('proxy-list-table')
    tb = t.find_element_by_tag_name('tbody')
    trs = tb.find_elements_by_tag_name('tr')
    for itr, tr in enumerate(trs):
        tds = tr.find_elements_by_tag_name('td')
        ip = ''
        port = 0
        protocol = ''
        country = ''
        for itd, td in enumerate(tds):
            print(itr,itd)
            if itd==0:
                country=td.text
            if itd==1:
                ip = td.text
            if itd==2:
                port = int(td.text)
            if itd==3:
                a = (ip, port, td.text, country)
                q.put(a)
    driver.quit()

def generateProxyListFromHideMyAss():
    driver = webdriver.Chrome()
    driver.get('http://proxylist.hidemyass.com/')
    while True:
        time.sleep(1)
        next = driver.find_element_by_class_name('next')
        nextclass = next.get_attribute('class')
        bNext = True
        if 'unavailable' in nextclass:
            bNext = False
        tbody = driver.find_element_by_tag_name('tbody')
        trs = tbody.find_elements_by_tag_name('tr')
        for tr in trs:
            tds = tr.find_elements_by_tag_name('td')
            ip = ''
            port = 0
            country = ''
            type = 'http'
            for idx, td in enumerate(tds):
                if idx==1:
                    sp = td.find_element_by_tag_name('span')
                    ip+= sp.text
                elif idx == 2:
                    port = td.text
                elif idx == 3:
                    country = td.text
                elif idx==6:
                    type = td.text
                    a = (ip, port, td.text, country)
                    q.put(a)
                    break
        if bNext:
            next.click()
        else:
            break
    driver.quit()


def generateProxyListFromHideIpMe():
    driver = webdriver.Chrome()
    driver.get('https://hideip.me/en/proxy/socks5list')
    while True:
        time.sleep(1)
        next = driver.find_element_by_id('next_plistproxy')
        bNext = True
        if 'unavailable' in nextclass:
            bNext = False
        tbody = driver.find_element_by_tag_name('tbody')
        trs = tbody.find_elements_by_tag_name('tr')
        for tr in trs:
            tds = tr.find_elements_by_tag_name('td')
            ip = ''
            port = 0
            country = ''
            type = 'http'
            for idx, td in enumerate(tds):
                if idx==1:
                    sp = td.find_element_by_tag_name('span')
                    ip+= sp.text
                elif idx == 2:
                    port = td.text
                elif idx == 3:
                    country = td.text
                elif idx==6:
                    type = td.text
                    a = (ip, port, td.text, country)
                    q.put(a)
                    break
        if bNext:
            next.click()
        else:
            break
    driver.quit()



def createProxyListTable():
    cnx = pymysql.connect(user='root', password=dbpassword,
                          host='127.0.0.1',
                          database='mypythondb')
    cursor = cnx.cursor()

    querys = ["create table `freeproxy` (`idx` int(10) unsigned not null auto_increment, " \
            "ip varchar(45) not null, port int(10) unsigned not null, country varchar(45), "\
            "protocol varchar(45), primary key(`idx`))",
            "ALTER TABLE `mypythondb`.`freeproxy` ADD UNIQUE INDEX `index1` (`ip` ASC, `port` ASC)",
            "alter table `mypythondb`.`freeproxy` add column `active` boolean default false",
            "alter table `mypythondb`.`freeproxy` add column `speed` int default 0",
            "alter table `mypythondb`.`freeproxy` add column `time_added` timestamp default '0000-00-00 00:00:00'",
            "alter table `mypythondb`.`freeproxy` add column `time_verified` timestamp default '0000-00-00 00:00:00'"]

    for query in querys:
        try:
            cursor.execute(query)
        except Exception as e:
            print(e)
    cursor.close()
    cnx.close()


class threadGenerateProxyList(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self.index = index
        return

    def run(self):
# comment out because this site is not working
#        try:
#             generateProxyListFromHideMyAss()
#        except:
#            pass
#        try:
#            generateProxyListFromFree_proxy_lists()
#        except Exception as e:
#            print(e)
#            pass
#        try:
#            generateProxyListFromFreeproxylists()
#        except:
#            pass
#        try:
#            generateProxyListFromProxynova()
#        except:
#            pass
#        try:
#            generateProxyListFromSocks_proxy_net()
#        except:
#            pass
        try:
            generateProxyListFromNordVpn()
        except:
            pass
        return

if __name__ == '__main__':
    createProxyListTable()

    t = threadGenerateProxyList(1)
    t.start()
    t.join()

    cnx = pymysql.connect(user='root', password=dbpassword, host='127.0.0.1', database='mypythondb')
    cursor = cnx.cursor()
    while True:
        try:
            a = q.get(True, 300)
            insert = "insert into `freeproxy` set ip='"+a[0]+"',port="+str(a[1])+", protocol='"+a[2]+"', country='"+a[3]+"', time_added=NOW()"
            cursor.execute(insert)
            cnx.commit()
        except queue.Empty:
            break
        except pymysql.err.IntegrityError as e:
            print(e)
            continue
        except pymysql.err.ProgrammingError as e:
            print(e)
            continue
        except Exception as e:
            print(e)
            continue
    cursor.close()
    cnx.close()
    quit(0)
