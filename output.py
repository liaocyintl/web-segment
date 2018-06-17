from urllib.parse import urljoin
import bs4
from lcypytools import common
import json
import urllib.request
import requests
import shutil
from PIL import Image

def __get_element(node):
    # for XPATH we have to count only for nodes with same type!
    length = 1
    for previous_node in list(node.previous_siblings):
        if isinstance(previous_node, bs4.element.Tag):
            length += 1
    if length > 1:
        return '%s:nth-child(%s)' % (node.name, length)
    else:
        return node.name

def __get_css_selector(node):
    path = [__get_element(node)]
    for parent in node.parents:
        if parent.name == "[document]":
            break
        path.insert(0, __get_element(parent))
    return ' > '.join(path)

def __get_css_background_image_urls(url, node, browser):
    nodes = [node]
    image_urls = []
    structure = ""
    for node in nodes:
        for child in node.children:
            if isinstance(child, bs4.element.Tag):
                nodes.append(child)
    for node in nodes:
        try:
            css_selector = __get_css_selector(node)
            relative_url = browser.find_element_by_css_selector(css_selector).value_of_css_property("background-image")
            if relative_url != "none":
                relative_url = relative_url.replace('url(', '').replace(')', '').replace('\'', '').replace('\"', '')
                relative_url = urljoin(url, relative_url)
                image_urls.append(relative_url)
        except:
            pass
    return image_urls

def output(url, browser, blocks, output_folder):
    segids = []
    rid = 0

    segs = dict()
    for i, block in enumerate(blocks):
        # texts
        texts, images, links, cssselectors = [], [], [], []

        for node in block:
            for text in node.stripped_strings:
                texts.append(text)

            # the images in css background
            background_image_urls = __get_css_background_image_urls(url, node, browser)
            for url in background_image_urls:
                dict_img = dict()
                dict_img["alt"] = ""
                dict_img["src"] = url
                images.append(dict_img)
            # the images in css background -- end

            for img in node.find_all("img"):
                dict_img = dict()
                if "src" in img.attrs:
                    dict_img["src"] = urljoin(url, img["src"])
                if "alt" in img.attrs:
                    dict_img["alt"] = img["alt"]
                images.append(dict_img)

            for link in node.find_all("a"):
                if "href" in link.attrs:
                    links.append({"href": urljoin(url, link["href"])})

            cssselectors.append(__get_css_selector(node))

        if len(texts) == 0 and len(images) == 0:
            continue
        # texts -- end

        lid = block[0]["lid"]

        if lid not in segids:
            segids.append(lid)
        sid = str(segids.index(lid))

        if sid not in segs:
            segs[sid] = {"segmentid": sid, "cssselector": __get_css_selector(block[0].parent), "records": []}
        # try:
        #         element = browser.find_element_by_css_selector(segs[sid]["cssselector"])
        #         segs[sid]["rect"] = element.rect
        #         pass
        #     except:
        #         pass

        segs[sid]["records"].append(
            {"recordid": rid, "texts": texts, "images": images, "cssselectors": cssselectors, "links": links})
        rid += 1

    json_data = {}
    json_data["segments"] = [value for key, value in segs.items()]
    json_data["url"] = url

    path = output_folder + "/"
    common.prepare_clean_dir(path)
    screenshot_path = path + "/screenshot.png"
    browser.save_screenshot(screenshot_path)
    common.save_json(path + "/result.json", json_data, encoding='utf-8')

    return json_data


def __encode_url(link):
    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(link)
    path = urllib.parse.quote(path)
    link = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
    return link


def __output_segment_images(browser, output_folder, json_data):
    path = output_folder + "segimgs/"
    common.prepare_clean_dir(path)
    for segment in json_data["segments"]:
        for record in segment["records"]:
            for index, cssselector in enumerate(record["cssselectors"]):
                file_name = path + str(record["recordid"]) + "_" + str(index) + ".png"
                try:
                    element = browser.find_element_by_css_selector(cssselector)
                    element_png = element.screenshot_as_base64
                    with open(file_name, 'wb') as f:
                        f.write(element_png.encode('ascii'))
                    pass
                except Exception as error:
                    print(error)
                    pass

def __encode_url(link):
    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(link)
    path = urllib.parse.quote(path)
    link = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
    return link

def output_images(output_folder, json_data, output_image_type="jpg"):
    tmp_path = output_folder + "/tmp/"
    path = output_folder + "/images/"
    common.prepare_clean_dir(tmp_path)
    common.prepare_clean_dir(path)
    for segment in json_data["segments"]:
        for record in segment["records"]:
            for i, image in enumerate(record["images"]):
                try:
                    original_extension = image["src"].split('/')[-1].split('.')[-1]
                    source_file_name = tmp_path + str(record["recordid"]) + "_" + str(i) + "." + original_extension
                    target_file_name = path + str(record["recordid"]) + "_" + str(i) + "." + output_image_type
                    # urllib.request.urlretrieve(__encode_url(image["src"]), source_file_name)

                    r = requests.get(__encode_url(image["src"]),
                                     stream=True, headers={'User-agent': 'Mozilla/5.0'})
                    if r.status_code == 200:
                        with open(source_file_name, 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)
                    else:
                        continue

                    im = Image.open(source_file_name)
                    # if white_image_background:
                    #     bg = Image.new("RGBA", im.size, (255, 255, 255))
                    #     bg.paste(im, im)
                    #     im = bg
                    rgb_im = im.convert('RGBA')
                    rgb_im.save(target_file_name)
                    # os.remove(source_file_name)
                except Exception as err:
                    pass
