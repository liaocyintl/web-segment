#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request
import bs4
import os
import errno
import json
from PIL import Image
import requests
import shutil


class Segmenter():
    def __init__(self, snapshot_width=1920):
        self.browser = webdriver.PhantomJS()
        self.browser.set_window_size(snapshot_width, 800)  # set the window size that you need
        self.parser = HTMLParser()

    def segment(self, url, output_folder="output", output_images=False, output_image_type="jpg",
                white_image_background=False):
        self.url = url
        self.output_folder = output_folder
        self.output_image_type = output_image_type
        self.white_image_background = white_image_background

        self.__crawler()

        self.__pruning()
        self.__partial_tree_matching()
        self.__backtracking()

        self.__output()

        if output_images:
            self.__output_images()
            # self.__output_segment_images()
        pass

    def __url_to_name(self):
        name = self.url
        name = name.replace("https://", "")
        name = name.replace("http://", "")
        name = name.replace("/", "_")
        name = name.replace(".", "_")
        return name

    def __prepare_output_folder(self, filename):
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def __crawler(self):
        self.browser.get(self.url)
        self.soup = BeautifulSoup(self.browser.page_source, 'html.parser')

    def __pruning(self):
        tagbody = self.soup.find("body")
        if tagbody is None:
            raise Exception("This HTML document has no <body> tag")
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
            # print(str(i) + "/" + str(len(self.allnodes)))

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

    def __output(self):

        segids = []
        rid = 0

        segs = dict()
        for i, block in enumerate(self.blocks):
            # texts
            texts, images, links, cssselectors = [], [], [], []

            for node in block:
                for text in node.stripped_strings:
                    texts.append(text)

                # the images in css background
                background_image_urls = self.__get_css_background_image_urls(node)
                for url in background_image_urls:
                    dict_img = dict()
                    dict_img["alt"] = ""
                    dict_img["src"] = url
                    images.append(dict_img)
                # the images in css background -- end


                for img in node.find_all("img"):
                    dict_img = dict()
                    if "src" in img.attrs:
                        dict_img["src"] = urljoin(self.url, img["src"])
                    if "alt" in img.attrs:
                        dict_img["alt"] = img["alt"]
                    images.append(dict_img)

                for link in node.find_all("a"):
                    if "href" in link.attrs:
                        links.append({"href": urljoin(self.url, link["href"])})

                cssselectors.append(self.__get_css_selector(node))

            if len(texts) == 0 and len(images) == 0:
                continue
            # texts -- end

            lid = block[0]["lid"]

            if lid not in segids:
                segids.append(lid)
            sid = str(segids.index(lid))

            if sid not in segs:
                segs[sid] = {"segmentid": sid, "cssselector": self.__get_css_selector(block[0].parent), "records": []}
            # try:
            #         element = self.browser.find_element_by_css_selector(segs[sid]["cssselector"])
            #         segs[sid]["rect"] = element.rect
            #         pass
            #     except:
            #         pass


            segs[sid]["records"].append(
                {"recordid": rid, "texts": texts, "images": images, "cssselectors": cssselectors, "links": links})
            rid += 1

        self.json_data = dict()
        self.json_data["segments"] = [value for key, value in segs.items()]
        self.json_data["url"] = self.url

        path = self.output_folder + "/"
        screenshot_path = path + "/screenshot.png"
        self.__prepare_output_folder(screenshot_path)
        self.browser.save_screenshot(screenshot_path)
        with open(path + "/result.json", 'w') as outfile:
            json.dump(self.json_data, outfile, ensure_ascii=False)

    def __encode_url(self, link):
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(link)
        path = urllib.parse.quote(path)
        link = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
        return link

    def __output_segment_images(self):
        path = self.output_folder + "segimgs/"
        self.__prepare_output_folder(path + "image.png")
        for segment in self.json_data["segments"]:
            for record in segment["records"]:
                for index, cssselector in enumerate(record["cssselectors"]):
                    file_name = path + str(record["recordid"]) + "_" + str(index) + ".png"
                    try:
                        element = self.browser.find_element_by_css_selector(cssselector)
                        element_png = element.screenshot_as_base64
                        with open(file_name, 'wb') as f:
                            f.write(element_png.encode('ascii'))
                        pass
                    except Exception as error:
                        print(error)
                        pass

    def __output_images(self):
        tmp_path = self.output_folder + "/tmp/"
        path = self.output_folder + "/images/"
        self.__prepare_output_folder(tmp_path + "image.png")
        self.__prepare_output_folder(path + "image.png")
        for segment in self.json_data["segments"]:
            for record in segment["records"]:
                for i, image in enumerate(record["images"]):
                    try:
                        original_extension = image["src"].split('/')[-1].split('.')[-1]
                        source_file_name = tmp_path + str(record["recordid"]) + "_" + str(i) + "." + original_extension
                        target_file_name = path + str(record["recordid"]) + "_" + str(i) + "." + self.output_image_type
                        # urllib.request.urlretrieve(self.__encode_url(image["src"]), source_file_name)

                        r = requests.get(self.__encode_url(image["src"]),
                                         stream=True, headers={'User-agent': 'Mozilla/5.0'})
                        if r.status_code == 200:
                            with open(source_file_name, 'wb') as f:
                                r.raw.decode_content = True
                                shutil.copyfileobj(r.raw, f)
                        else:
                            continue

                        im = Image.open(source_file_name)
                        if self.white_image_background:
                            bg = Image.new("RGBA", im.size, (255, 255, 255))
                            bg.paste(im, im)
                            im = bg
                        rgb_im = im.convert('RGBA')
                        rgb_im.save(target_file_name)
                        # os.remove(source_file_name)
                    except Exception as err:
                        pass


if __name__ == "__main__":
    spliter = Segmenter(snapshot_width=1920)
    spliter.segment("http://www.hokepon.com/", "data/web/24/", output_images=True, white_image_background=True)
