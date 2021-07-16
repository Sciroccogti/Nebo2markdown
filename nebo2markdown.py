import argparse
import os
import re

import html2markdown
from bs4 import BeautifulSoup

from mathconverter.converter import mathml2latex_yarosh

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="path to input .html", type=str, required=True)
    parser.add_argument(
        "-o", "--output", help="path to output .md", type=str, required=True)
    args = parser.parse_args()

    htmlFile = open(args.url, encoding="utf-8")
    bs = BeautifulSoup(htmlFile.read(), "html.parser")
    markdownFile = open(args.output, encoding="utf-8", mode="w")
    bs = BeautifulSoup(htmlFile.html.html, "lxml")
    print(bs.prettify())
    pageHTML = bs.find("main", class_="page-html")
    contents = pageHTML.contents
    assert(len(contents) == 1)
    mainDiv = contents[0]
    for block in mainDiv:
        if (block == "\n"):
            continue
        if ("block-text" in block.attrs["class"]):
            for text in block.contents:
                try:
                    markdownFile.write(html2markdown.convert(text))
                except:
                    t = text.__unicode__()
                    t = re.sub(r"<span.*?>", "", t)
                    t = re.sub(r"</span>", "", t)
                    markdownFile.write(html2markdown.convert(t) + os.linesep)
        elif ("block-math" in block.attrs["class"]):
            mathML = block.math
            latex = mathml2latex_yarosh(mathML.__unicode__())
            markdownFile.write(latex + os.linesep)

    markdownFile.close()
