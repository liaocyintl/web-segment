
import bs4

def pruning(html):
    tagbody = html.find("body")
    if tagbody is None:
        raise Exception("This HTML document has no <body> tag")
    tagbody["lid"] = str(-1)
    tagbody["sn"] = str(1)
    allnodes = [tagbody]
    i = 0
    while len(allnodes) > i:
        children = []
        for child in allnodes[i].children:
            if isinstance(child, bs4.element.Tag):
                children.append(child)
        sn = len(children)

        for child in children:
            child["lid"] = str(i)
            child["sn"] = str(sn)
            allnodes.append(child)
        i += 1
    return allnodes