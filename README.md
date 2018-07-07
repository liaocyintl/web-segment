Introduction
======

Data on a webpage are composed of semi-structured data, which cannot be directly processed.
We propose this web segment algorithm, which converts a HTML document into structured data.
Through this algorithm, a HTML document is segmented into "Segments" and "Records" corresponding to "Tables" and "Records" in a structured database, respectively.

For example, a webpage shown as follow is segmented into "Segment 1" that contains "Record 1" and "Record2",
and "Segment 2" that contains "Record 3" and "Record 4".

![](imgs\c66da037.png)

Corresponding to a database, they should be:

Segment 1:

|  id  |  text  |
| ---- | ---- |
|  1  |  July 2, 2018 Nagoya University's Offices to Be Closed on August 13 and... |
|  2  |  To All Students, Faculty Members, and Staff Members of Nagoya Univ...  |

Segment 2:

|  id  |  text  |
| ---- | ---- |
|  3  |  Prof. Masaru Hori of the Institutes of Innovation for Future Society... |
|  4  |  Former Nagoya University Associate Prof. Masaki Kashiwara Selected...  |


Quick Started
======

- Our Testing Environment (Also can be ran on Linux or Mac)
    - OS: Microsoft Windows 10 Pro
    - Python: 3.6.5
    - Chrome: 67.0.3396.79 (Official Build) (64-bit)
    - Chrome-driver: 2.4

- Clone the code

```bash
$ git clone --recursive https://github.com/liaocyintl/WebSegment.git
```

- Config **setting.py**
    - CHROME_BINARY_LOCATION is the path of Chrome EXE, which we used as the headless brower.
        - Windows: "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" on default
        - Linux(Ubuntu): should be "/usr/bin/google-chrome" see [here](https://qiita.com/shinsaka/items/37436e256c813d277d6d) for detail
        - Mac OS: should be "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary" see [here](https://duo.com/decipher/driving-headless-chrome-with-python) for detail
    - DRIVER_PATH: You will need to download the ChromeDriver executable from [here](http://chromedriver.storage.googleapis.com/index.html?path=2.4/) corresponding to your OS.

- Try to segment a webpage in the sample code **demo.py**

```python
from segment import Segment
spliter = Segment()
spliter.segment(url="http://www.sukiya.jp/", output_folder="data/sukiya", is_output_images=True)
```

Parameters:

|  Parameter  |  Description  |
| ---- | ---- |
|  url  |  The URL of webpage that you want to segment |
|  output_folder  |  The folder path you want to output segment results  |
|  is_output_images  |  Output web images or not, default 'False' |


Output
========

## result.json

The file result.json in output folder is the main segment result.
```json
{
  "title":"すき家",
  "url":"http://www.sukiya.jp/",
  "segments": [
    {
      "records": [
        {
          "texts": ["すき家"],
          "css_selectors": [
            "html > body:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div > div > div"
          ],
          "links": [
            {
              "href": "http://www.sukiya.jp/"
            }
          ],
          "images": [
            {
              "alt": "",
              "src": "http://www.sukiya.jp/common/img/hd_logo.png",
              "path": "data/sukiya/images/66_0.png",
              "bg_color": "255,255,255"
            }
          ],
          "record_id": 66
        }
      ],
      "segment_id": 13,
      "css_selector": "html > body:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div > div"
    }
  ]
}
```

- title: the title of the webpage
- url: the URL of the webpage
- segments: an array of segments, which contain records.
    - segment_id: an unique ID of this record in result.json
    - css_selector: the CSS selector of this segment (A segment has only one root element)
    - records: an array of records in a segments.
        - record_id: an unique ID of this record in result.json
        - css_selectors: an array of all CSS selectors of all elements in this record (A record may has multiple sibling elements)
        - texts: an array of texts in this record
        - links: an array of hyperlinks in this record
            - href: the 'href' attribute of this link (absolute URL)
        - images: an array of images in this record
            - alt: the 'alt' attribute of this image
            - src: the 'src' attribute of this image (absolute URL)
            - path: the local path where the image is archived to only when set is_output_images to "True"
            - bg_color: the R,G,B background color of the image

## screenshot.png

A screenshot of this webpage.

## images (Folder)
If set "is_output_images" to "True", the folder will be generated.
Web images are saved in it.
The file name is compose as "record id + '_' + seq. in this record".
The path can be found at segments.records.images.path in the result.json.

Some Algorithm Details
========
- Some web images are hidden in the element's background image attribute defined in its Cascading Style Sheets (CSS). 
The crawler scans all nodes in the HTML document and extracts the background image if the node has one. 
- A web image might be a PNG image with a transparent background. 
It relies on the background color of its parent nodes to form part of the color scheme of the logo. 
Therefore, when the crawler finds an image type capable of having transparency, such as a PNG, the crawler then scans all its parent nodes in the proper sequence to locate the one which has the same background color attribute in CSS, and converts the PNG image into JPG with the matching background color. 


## Cite
If you like this work please cite our paper
```text
@article{websegment2,
  title={An Event Data Extraction Method Based on HTML Structure Analysis and Machine Learning},
  author={Liao, Chenyi and Hiroi, Kei and Kaji, Katsuhiko and Kawaguchi, Nobuo},
  journal={Computer Software and Applications Conference (COMPSAC)},
  volume={3},
  pages = {217-222},
  year={2015}
}
```