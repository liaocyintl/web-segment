from crawler import (crawl_html_doc)
from pruning import (pruning)
from partial_tree_matching import (partial_tree_matching)
from backtracking import (backtracking)
from output import (output, output_images)

def segment(url, output_folder="output", output_image_type="jpg"):
    html, browser = crawl_html_doc(url)
    allnodes = pruning(html)
    allnodes, blocks = partial_tree_matching(allnodes)

    allnodes, blocks = backtracking(allnodes, blocks)

    json_data = output(url, browser, blocks, output_folder)
    output_images(output_folder, json_data, output_image_type=output_image_type)

    print("Segmented: ", url)

if __name__ == "__main__":
    segment("https://www.yahoo.com/")
