from crawler import (mark_extracted)

def backtracking(allnodes, blocks):
    for node in allnodes:
        if (node.name != "body") and (node.parent is not None) and ('extracted' not in node.attrs) and (
                'extracted' in node.parent.attrs):
            blocks.append([node])
            mark_extracted([node])
    return allnodes, blocks