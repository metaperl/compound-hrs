#!/usr/bin/python

# system
from collections import defaultdict
import pdb
import pprint
import sys
import time
import traceback

# pypi
from splinter import Browser

# local
import user as userdata


pp = pprint.PrettyPrinter(indent=4)

base_url = 'http://www.hourlyrevshare.net'
action_path = dict(
    login = "index.php?p=login",
    buy_shares = 'index.php?p=buy_shares'
)

def url_for_action(action):
    return "{0}/{1}".format(base_url,action_path[action])

pay_via = dict(
    stp='1',
    pm='5',
    lr='6',
    egopay='10'
)

class Entry(object):

    def __init__(self, user, browser, url):
        self.user=user
        self.browser=browser
        self.url=url

    def click_submit_button(self):
        button = self.browser.find_by_xpath('//*[@type="submit"]')
        button.click()

    def wait_for_captcha_solution(self):
        browser.visit(base_url)
        time.sleep(15)
        self.click_submit_button()

    def login(self):
        browser.visit(url_for_action('login'))
        self.browser.fill('user', self.user['username'])
        self.browser.fill('pass', self.user['password'])
        self.click_submit_button()

    def extract_e_currencies(self):
        trs = self.browser.find_by_tag('tr')
        #print "tbody: {0}".format(trs)

        desired_indices = (1,3,4)
        index = -1
        index_to_merchant = {
            1 : 'stp',
            3 : 'lr',
            4 : 'egopay'
        }
        self.stats = dict(
            (v, dict(balance=None,action=None))
            for k,v in index_to_merchant.iteritems()
        )
        for tr in trs:
            tds = tr.find_by_tag('td')
            if len(tds) == 6:
                index += 1
                if index in desired_indices:
                    m = index_to_merchant[index]
                    self.stats[m]['balance'] = float(tds[2].value[1::])

    def compound(self, processor, amount):
        # Click Buy Shares
        url = action_path['buy_shares']
        print "URL to buy share: {0}".format(url)
        self.browser.visit(url_for_action('buy_shares'))
        button = self.browser.find_by_xpath(
            '//input[@value="1"]'
        )
        button.click()
        self.click_submit_button()

        # Fill in amount of shares to buy
        shares = str(int(amount))
        self.browser.fill('units', shares)

        # Click Site/Cash Balance
        button = self.browser.find_by_id('pay_via_0')
        button.click()

        # Choose processor
        self.browser.select('paypro', pay_via[processor])

        self.click_submit_button()


with Browser() as browser:

    for user in userdata.users:
        e = Entry(user, browser, '')
        e.wait_for_captcha_solution()
        e.login()
        e.extract_e_currencies()
        pp.pprint(e.stats)
        for processor,pd in e.stats.items():
            balance = pd['balance']
            print "Processor: {0} has {1}".format(processor,balance)
            if balance >= 5:
                print "\tCompounding"
                e.compound(processor, balance)

    time.sleep(20)
