#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from lcypytools import common
import bs4

import requests
import shutil
import setting


class Segment:
    def __init__(self):
        options = Options()
        options.binary_location = setting.CHROME_BINARY_LOCATION
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=options, executable_path=setting.DRIVER_PATH)
        self.browser.set_window_size(setting.SCREEN_WIDTH, 800)  # set the window size that you need
        self.parser = HTMLParser()

    def segment(self, url, output_folder="output", output_images=False):
        self.url = url
        self.output_folder = self.remove_slash(output_folder)
        self.log = common.log()

        self.log.write("Crawl HTML Document from %s" % self.url)
        self.__crawler()

        self.log.write("Run Pruning on %s" % self.url)
        self.__pruning()
        self.log.write("Run Partial Tree Matching on %s" % self.url)
        self.__partial_tree_matching()
        self.log.write("Run Backtracking on %s" % self.url)
        self.__backtracking()

        self.log.write("Output Result JSON File on  %s" % self.url)
        self.__output()

        if output_images:
            self.log.write("Output Images on  %s" % self.url)
            self.__output_images()

        self.log.write("Finished on  %s" % self.url)

    def __crawler(self):
        self.browser.get(self.url)
        self.soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        page_height = self.browser.find_element_by_tag_name("body").rect["height"]
        self.browser.set_window_size(setting.SCREEN_WIDTH, page_height)

        common.prepare_clean_dir(self.output_folder)
        self.browser.save_screenshot(self.output_folder + "/screenshot.png")

    def __pruning(self):
        tagbody = self.soup.find("body")
        tagbody["lid"] = str(-1)
        tagbody["sn"] = str(1)
        self.allnodes = [tagbody]
        i = 0
        while len(self.allnodes) > i:
            children = []
            for child in self.allnodes[i].children:
                if isinstance(child, bs4.element.Tag):
                    children.append(child)
            sn = len(children)

            for child in children:
                child["lid"] = str(i)
                child["sn"] = str(sn)
                self.allnodes.append(child)
            i += 1
        pass

    def __partial_tree_matching(self):
        self.blocks = []

        lid_old = -2

        i = 0
        while i < len(self.allnodes):

            node = self.allnodes[i]

            if 'extracted' in node.attrs:
                i += 1
                continue
            sn, lid = int(node["sn"]), int(node["lid"])

            if lid != lid_old:
                max_window_size = int(sn / 2)
                lid_old = lid

            for ws in range(1, max_window_size + 1):

                pew, cew, new = [], [], []

                for wi in range(i - ws, i + 2 * ws):

                    if wi >= 0 and wi < len(self.allnodes) and int(self.allnodes[wi]["lid"]) == lid:
                        cnode = self.allnodes[wi]
                        if wi >= i - ws and wi < i:
                            pew.append(cnode)
                        if wi >= i and wi < i + ws:
                            cew.append(cnode)
                        if wi >= i + ws and wi < i + 2 * ws:
                            new.append(cnode)

                        pass

                isle = self.__compare_nodes(pew, cew)
                isre = self.__compare_nodes(cew, new)

                if isle or isre:
                    self.blocks.append(cew)
                    i += ws - 1
                    max_window_size = len(cew)
                    self.__mark_extracted(cew)
                    break
            i += 1
        pass

    def __mark_extracted(self, nodes):
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

    def __compare_nodes(self, nodes1, nodes2):
        if len(nodes1) == 0 or len(nodes2) == 0:
            return False

        return self.__get_nodes_children_structure(nodes1) == self.__get_nodes_children_structure(nodes2)
        pass

    def __get_nodes_children_structure(self, nodes):
        structure = ""
        for node in nodes:
            structure += self.__get_node_children_structure(node)
        return structure

    def __get_node_children_structure(self, node):
        nodes = [node]
        structure = ""
        for node in nodes:
            for child in node.children:
                if isinstance(child, bs4.element.Tag):
                    nodes.append(child)
            structure += node.name
        return structure

    def __backtracking(self):

        for node in self.allnodes:
            if (node.name != "body") and (node.parent is not None) and ('extracted' not in node.attrs) and (
                    'extracted' in node.parent.attrs):
                self.blocks.append([node])
                self.__mark_extracted([node])
        pass

    def __get_element(self, node):
        # for XPATH we have to count only for nodes with same type!
        length = 1
        for previous_node in list(node.previous_siblings):
            if isinstance(previous_node, bs4.element.Tag):
                length += 1
        if length > 1:
            return '%s:nth-child(%s)' % (node.name, length)
        else:
            return node.name

    def __get_css_selector(self, node):
        path = [self.__get_element(node)]
        for parent in node.parents:
            if parent.name == "[document]":
                break
            path.insert(0, self.__get_element(parent))
        return ' > '.join(path)

    def __get_css_background_image_urls(self, node):
        nodes = [node]
        image_urls = []
        structure = ""
        for node in nodes:
            for child in node.children:
                if isinstance(child, bs4.element.Tag):
                    nodes.append(child)
        for node in nodes:
            try:
                css_selector = self.__get_css_selector(node)
                url = self.browser.find_element_by_css_selector(css_selector).value_of_css_property("background-image")
                if url != "none":
                    url = url.replace('url(', '').replace(')', '').replace('\'', '').replace('\"', '')
                    url = urljoin(self.url, url)
                    image_urls.append(url)
            except:
                pass
        return image_urls

    def __get_css_selector(self, node):
        path = [self.__get_element(node)]
        for parent in node.parents:
            if parent.name == "[document]":
                break
            path.insert(0, self.__get_element(parent))
        return ' > '.join(path)

    def __rgba2RGBA(self, rgba):
        try:
            rgba = rgba.replace("rgba(", "").replace(")", "")
            (R, G, B, A) = tuple(rgba.split(","))
            return int(R), int(G), int(B), float(A)
        except:
            return 0, 0, 0, 0

    def __get_css_background_color(self, node):
        nodes = [node]
        for p in node.parents:
            nodes.append(p)

        (R, G, B) = (255, 255, 255)
        for node in nodes:
            try:
                css_selector = self.__get_css_selector(node)
                color = self.browser.find_element_by_css_selector(css_selector).value_of_css_property(
                    "background-color")

                Rn, Gn, Bn, A = self.__rgba2RGBA(color)

                if A == 1:
                    (R, G, B) = (Rn, Gn, Bn)
                    break
            except:
                pass
        return R, G, B

    def __output(self):

        segids = []
        rid = 0

        segs = dict()
        for i, block in enumerate(self.blocks):
            # texts
            texts, images, links, cssselectors = [], [], [], []

            for node in block:
                # extract text from node
                for text in node.stripped_strings:
                    texts.append(text)
                # extract text from node -- end

                # extract images in css background
                background_image_urls = self.__get_css_background_image_urls(node)
                for url in background_image_urls:
                    dict_img = dict()
                    dict_img["alt"] = ""
                    dict_img["src"] = urljoin(self.url, url)
                    r, g, b = self.__get_css_background_color(node)
                    dict_img["bg_color"] = "%d,%d,%d" % (r, g, b)
                    images.append(dict_img)
                # extract images in css background -- end

                # extract images in <img> element
                for img in node.find_all("img"):
                    dict_img = dict()
                    if "src" in img.attrs:
                        dict_img["src"] = urljoin(self.url, img["src"])
                    if "alt" in img.attrs:
                        dict_img["alt"] = img["alt"]
                    images.append(dict_img)
                    r, g, b = self.__get_css_background_color(img)
                    dict_img["bg_color"] = "%d,%d,%d" % (r, g, b)
                # extract images in <img> element

                # extract hyperlink from node
                for link in node.find_all("a"):
                    if "href" in link.attrs:
                        links.append({"href": urljoin(self.url, link["href"])})
                # extract hyperlink from node -- end

                cssselectors.append(self.__get_css_selector(node))

            if len(texts) == 0 and len(images) == 0:
                continue

            lid = block[0]["lid"]

            if lid not in segids:
                segids.append(lid)
            sid = str(segids.index(lid))

            if sid not in segs:
                segs[sid] = {"segment_id": sid, "css_selector": self.__get_css_selector(block[0].parent), "records": []}

            segs[sid]["records"].append(
                {"record_id": rid, "texts": texts, "images": images, "css_selectors": cssselectors, "links": links})
            rid += 1

        self.json_data = dict()
        self.json_data["segments"] = [value for key, value in segs.items()]
        self.json_data["url"] = self.url
        self.json_data["title"] = self.browser.title

        common.save_json(self.output_folder + "/result.json", self.json_data, encoding=setting.OUTPUT_JSON_ENCODING)

    def __output_images(self):
        tmp_path = self.output_folder + "/tmp"
        path = self.output_folder + "/images"
        common.prepare_clean_dir(tmp_path)
        common.prepare_clean_dir(path)
        for segment in self.json_data["segments"]:
            for record in segment["records"]:
                for i, image in enumerate(record["images"]):
                    try:
                        file_name = "%s_%s" % (record["record_id"], i)
                        source_file_name_only = tmp_path + "/" + file_name
                        original_extension = image["src"].split('/')[-1].split('.')[-1].split("?")[0]
                        source_file_name = source_file_name_only + "." + original_extension
                        target_file_name = path + "/" + file_name + "." + setting.OUTPUT_IMAGE_TYPE

                        r = requests.get(image["src"], stream=True, headers={'User-agent': 'Mozilla/5.0'})
                        if r.status_code == 200:
                            with open(source_file_name, 'wb') as f:
                                r.raw.decode_content = True
                                shutil.copyfileobj(r.raw, f)
                        else:
                            continue

                        [R, G, B] = [int(a) for a in image["bg_color"].split(",")]
                        im = Image.open(source_file_name).convert('RGBA')
                        bg = Image.new("RGB", im.size, (R, G, B))
                        bg.paste(im, im)
                        im = bg
                        im.save(target_file_name)

                        image["path"] = target_file_name
                    except Exception:
                        pass

        common.save_json(self.output_folder + "/result.json", self.json_data, encoding=setting.OUTPUT_JSON_ENCODING)

        shutil.rmtree(tmp_path)

    def remove_slash(self, path):
        for i in range(len(path)):
            if path.endswith('/'):
                path = path[:-1]
            if path.endswith('\\'):
                path = path[:-1]
        return path
