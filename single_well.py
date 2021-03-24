"""
登录中澳网站下载指定井号、指定开始日期、指定结束日期的生产动态数据
"""
import time
import re
from lxml import etree
from selenium import webdriver
import pandas as pd


class SpiderSinoWellGas(object):
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

    def get_singwell(self, well, start, end):
        """访问url"""
        url = "http://125.208.20.50/showQueryReport.jsp?jh={}&qsrq={}&jzrq={}&reportName={}%E6%97%A5%E6%95%B0%E6%8D%AE&report=query%2Fqicangdongtai%2Fdanjing%2Freport_query_QCDT_DJ_RSJ.raq"
        self.driver.get(url=url.format(well, start, end, well))
        return self.driver.page_source

    def parse_html(self, well):
        """解析并下载数据"""
        parse_html = etree.HTML(self.driver.page_source)
        down_str = parse_html.xpath('//body/script[@language="javascript"][3]')[0].text
        pattern = r'[\s\S]*function[\s\S]*saveAsExcel[\s\S]*var[\s\S]*address[\s\S]*=[\s\S]*"(.*?)";[\s\S]*document[\s\S]*}'
        address = re.findall(pattern, down_str)[0]
        driver2 = webdriver.Chrome()
        print(well, address)
        driver2.get(address)
        return driver2

    def start(self, df):
        """
        df: 3列，分别是井号、开始、结束
        """
        # 1.登录
        self.login()
        time.sleep(10)
        for row in df.index:
            well = df.loc[row, '井号']
            start = df.loc[row, '开始']
            end = df.loc[row, '结束']
            self.get_singwell(well, start, end)
            self.parse_html(well)


if __name__ == '__main__':
    path = r'E:\临兴西日报\linxing_daily_pro_spider\下载指定单井日期数据.xlsx'
    df = pd.read_excel(io=path, sheet_name=6)
    df = df.astype('str').applymap(lambda x: x.replace(' ', '').replace('\n', ''))
    SpiderSinoWellGas().start(df)
