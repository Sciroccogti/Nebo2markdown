import argparse
from io import TextIOWrapper
import os
import re

import html2text
from bs4 import BeautifulSoup
from bs4.element import Tag

from mathconverter.converter import mathml2latex_yarosh

h2t = html2text.HTML2Text()
h2t.body_width = 0

def htmlUnparse(html: Tag, markdownFile: TextIOWrapper, isRow: bool = False):
    for block in html:
        if (block == "\n"):
            continue
        if ("block-text" in block.attrs["class"]):
            for text in block.contents:
                if (text == "\n"):
                    continue
                try:
                    markdownFile.write(h2t.handle(text))
                except:
                    t = text.__unicode__()
                    t = re.sub(r"<span.*?>", "", t)
                    t = re.sub(r"</span>", "", t)
                    markdownFile.write(h2t.handle(t))
        elif ("block-math" in block.attrs["class"]):
            mathML = block.math
            latex = mathml2latex_yarosh(mathML.__unicode__())
            if (not isRow):
                # mark as full line formula
                latex = '$' + latex + '$'
            markdownFile.write(latex)
        elif ("row" in block.attrs["class"]):
            for col in block.contents:
                if (col == "\n"):
                    continue
                for cls in col.attrs["class"]:
                    if (cls.startswith("col")):
                        htmlUnparse(col, markdownFile, True)
        if (not isRow):
            markdownFile.write(os.linesep)
        else:
            markdownFile.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="path to input .html", type=str, required=True)
    parser.add_argument(
        "-o", "--output", help="path to output .md", type=str, required=True)
    args = parser.parse_args()

    htmlFile = open(args.input, encoding="utf-8")
    bs = BeautifulSoup(htmlFile.read(), "html.parser")
    markdownFile = open(args.output, encoding="utf-8", mode="w")
    pageHTML = bs.find("main", class_="page-html")
    contents = pageHTML.contents
    assert(len(contents) == 1)
    mainDiv = contents[0]
    htmlUnparse(mainDiv, markdownFile)
    markdownFile.close()
