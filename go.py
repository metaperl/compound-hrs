#!/usr/bin/python

from collections import defaultdict

import pdb
import sys
import traceback

from splinter import Browser
import user as userdata


base_url = 'http://www.hourlyrevshare.net'
action_path = dict(
    login = "index.php?p=login"
)

def url_for_action(action):
    return "{0}/{1}".format(base_url,action_path[action])


class Entry(object):

    @staticmethod
    def mystyle(url):
        return "singlehood" in url

    def __init__(self, user, browser, url):
        self.user=user
        self.browser=browser
        self.url=url
        self.email_name_attribute = "data[GiveawayEntry][email]"

    def submit_contact_info(self):
        button = self.browser.find_by_xpath('//*[@class="submit button"]')
        button.click()

    def login(self):
        self.browser.fill('user', self.user['username'])
        self.browser.fill('pass', self.user['password'])
        button = self.browser.find_by_xpath('//*[@type="submit"]')
        print "Button: {0}".format(button)
        button.click()


    def extract_e_currencies(self):
        trs = self.browser.find_by_tag('tr')
        print "tbody: {0}".format(trs)

        desired_indices = (1,3,4)
        index = -1
        index_to_merchant = {
            1 : 'stp',
            3 : 'lr',
            4 : 'egopay'
        }
        stats = dict((v, dict(balance=None,action=None)) for k,v in index_to_merchant.iteritems())
        for tr in trs:
            tds = tr.find_by_tag('td')
            if len(tds) == 6:
                index += 1
                if index in desired_indices:
                    m = index_to_merchant[index]
                    stats[m]['balance'] = tds[2].value
                    stats[m]['action'] = tds[5].value
        print stats


    def enter_email(self):
        self._enter_email()
        self.click_email_submit()

    def enter_contact_info(self):
        for k, v in self.user.items():
            if k == 'state': continue
            field_name = "data[GiveawayEntry][{0}]".format(k)
            if k == 'address' or k == 'city' or k == 'zip':
                field_name = "data[GiveawayEntryAddress][{0}]".format(k)
            self.browser.fill(field_name, v)
        e = self.browser.find_by_xpath(
            '//*[@value="{0}"]'.format(self.user['state'])
        )
        e._element.click()
        self.submit_contact_info()

    def confirm_info(self):
        self.browser.find_by_xpath('//*[@class="button button-yes"]').click()

    def find_accept_button(self):
        return self.browser.find_by_xpath('//*[@class="button"]').click()

    def accept_terms(self):
        button = self.find_accept_button()
        button.click()


    def enter_contest(self):
        print "\tEntering contest {0}".format(self.url)
        self.browser.visit(self.url)
        self.enter_email()
        self.enter_contact_info()
        self.confirm_info()
        self.accept_terms()



def different_browser_flow(url):
    strs = "500-happy hummus kenra stiletto lillian chicco chanel anolon".split()
    return any(s in url for s in strs)

with Browser() as browser:

    initial_url = url_for_action('login')
    print initial_url
    browser.visit(initial_url)

    for user in userdata.users:
        e = Entry(user, browser, '')
        e.login()
        e.extract_e_currencies()
