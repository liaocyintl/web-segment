
from crawler import (compare_nodes, mark_extracted)

def partial_tree_matching(allnodes):
    blocks = []

    lid_old = -2

    i = 0
    while i < len(allnodes):
        node = allnodes[i]

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

                if wi >= 0 and wi < len(allnodes) and int(allnodes[wi]["lid"]) == lid:
                    cnode = allnodes[wi]
                    if wi >= i - ws and wi < i:
                        pew.append(cnode)
                    if wi >= i and wi < i + ws:
                        cew.append(cnode)
                    if wi >= i + ws and wi < i + 2 * ws:
                        new.append(cnode)

                    pass

            isle = compare_nodes(pew, cew)
            isre = compare_nodes(cew, new)

            if isle or isre:
                blocks.append(cew)
                i += ws - 1
                max_window_size = len(cew)
                mark_extracted(cew)
                break
        i += 1
    return allnodes, blocks