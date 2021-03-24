"""
登录中澳网站下载某个日期数据
"""
import time
import re
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd


class SpiderSinogas(object):
    def __init__(self):
        self.url = 'http://125.208.20.50/login.jsp'
        self.login_name = '华夏吉泰'
        self.pwd = '123456'
        self.driver = webdriver.Chrome()

    def login(self):
        # 1.登录
        self.driver.get(self.url)
        name = self.driver.find_element_by_xpath('//*[@id="loginName"]')
        pwd = self.driver.find_element_by_xpath('//*[@id="password"]')
        click = self.driver.find_element_by_xpath('//*[@id="loginForm"]//img[@src="images/desktop/button_login.png"]')
        name.send_keys(self.login_name)
        pwd.send_keys(self.pwd)
        click.click()

    def click_baobiao(self):
        # 2.点击报表
        self.driver.switch_to.frame('barPanel')
        baobiao = self.driver.find_element_by_xpath('//a[@id="list0103"]')
        baobiao.click()

    def presence_wait(self, id_name):
        expect_condition = EC.presence_of_element_located((By.ID, id_name))
        wait = WebDriverWait(self.driver, 60)
        target_presence = wait.until(expect_condition)
        return target_presence

    def get_daily_production(self, date):
        url = 'http://125.208.20.50/showQueryReport.jsp?yqtName=%E4%B8%B4%E5%85%B4&yqtCode=LX&rq={}&reportName=%E4%B8%B4%E5%85%B4%E6%97%A5%E6%8A%A5&report=query%2Fqicangdongtai%2Fbaobiao%2Freport_query_QCDT_BB_RB.raq'
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
        self.driver.get(url=url.format(date))
        return self.driver.page_source

    def parse_html(self, date):
        parse_html = etree.HTML(self.driver.page_source)
        down_str = parse_html.xpath('//body/script[@language="javascript"][3]')[0].text
        pattern = r'[\s\S]*function[\s\S]*saveAsExcel[\s\S]*var[\s\S]*address[\s\S]*=[\s\S]*"(.*?)";[\s\S]*document[\s\S]*}'
        address = re.findall(pattern, down_str)[0]
        driver2 = webdriver.Chrome()
        print(date, address)
        driver2.get(address)
        return driver2

    def start(self, dates):
        # 1.登录
        self.login()
        # 2.点击'报表'
        self.presence_wait('barPanel')
        self.click_baobiao()
        time.sleep(10)
        # 3.生产数据
        for date in dates:
            self.get_daily_production(date)
            self.parse_html(date)


if __name__ == '__main__':
    path = r'E:\临兴西日报\linxing_daily_pro_spider\日期.xlsx'
    dates_ = pd.read_excel(io=path)['日期'].astype('str').to_list()
    SpiderSinogas().start(dates_)

