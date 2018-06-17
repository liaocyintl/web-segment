#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
import bs4
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

SNAPSHOP_WIDTH = 1280
# chrome executable file, you can download from https://www.google.co.jp/chrome/browser
CHROME_BINARY_LOCATION = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
# download driver file from https://chromedriver.storage.googleapis.com/index.html?path=2.40/
DRIVER_PATH = "driver/chromedriver.exe"


def crawl_html_doc(url):
    options = Options()
    options.binary_location = CHROME_BINARY_LOCATION
    options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=options, executable_path=DRIVER_PATH)
    browser.set_window_size(SNAPSHOP_WIDTH, 800)  # set the window size that you need
    browser.get(url)
    html = BeautifulSoup(browser.page_source, 'html.parser')
    return html, browser

def get_node_children_structure(node):
    nodes = [node]
    structure = ""
    for node in nodes:
        for child in node.children:
            if isinstance(child, bs4.element.Tag):
                nodes.append(child)
        structure += node.name
    return structure

def get_nodes_children_structure(nodes):
    structure = ""
    for node in nodes:
        structure += get_node_children_structure(node)
    return structure

def compare_nodes(nodes1, nodes2):
    if len(nodes1) == 0 or len(nodes2) == 0:
        return False

    return get_nodes_children_structure(nodes1) == get_nodes_children_structure(nodes2)
    pass

def mark_extracted(nodes):
    for node in nodes:
        node["extracted"] = ""
        lid = node["lid"]
        parent = node
        while parent.parent is not None:
            parent = parent.parent
            parent["extracted"] = ""
            parent["sid"] = lid

        nodecols = [node]
        for nodecol in nodecols:
            for child in nodecol.children:
                if isinstance(child, bs4.element.Tag):
                    nodecols.append(child)
            nodecol["extracted"] = ""


if __name__ == "__main__":
    html = crawl_html_doc("https://www.yahoo.com/")
    print(html)
