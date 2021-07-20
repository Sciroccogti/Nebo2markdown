import argparse
import os
import re
import time
from io import TextIOWrapper

from bs4 import BeautifulSoup
from bs4.element import Tag

import html2text
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
                    # regard <span style="background-color:rgba(255,221,51,0.4);"> as <mark>
                    pattern = r"<span(?:.|\n)[^>]*?background-color(?:.|\n)[^>]*?rgba\(255,221,51,0.4\)(?:.|\n)[^>]*?>(.[^>]*?)</span>"
                    t = re.sub(pattern, r"==\1==", t)
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
        "-i", "--input", help="path to input .html", type=str)
    parser.add_argument(
        "-u", "--url", help="url of published Nebo page", type=str)
    parser.add_argument(
        "-o", "--output", help="path to output .md", type=str, required=True)
    args = parser.parse_args()

    if (args.input != None):
        htmlFile = open(args.input, encoding="utf-8")
        bs = BeautifulSoup(htmlFile.read(), "html.parser")
    elif (args.url != None):
        from selenium import webdriver
        try:
            browser = webdriver.Chrome()
        except Exception as err:
            print("Chrome: " + str(err))
            try:
                browser = webdriver.Firefox()
            except Exception as err:
                print("FireFox: " + str(err))
                try:
                    browser = webdriver.Edge()
                except Exception as err:
                    print("Microsoft Edge Driver: " + str(err))
                    print("No valid webdriver detected by selenium.")
                    print("See https://pypi.org/project/selenium/#Drivers")
                    exit(-1)

        browser.get(args.url)
        # browser.execute_script(
        #     "window.scrollTo(0, document.body.scrollHeight);"
        #     "var lenOfPage=document.body.scrollHeight;"
        #     "return lenOfPage;")
        time.sleep(1)  # wait for JavaScript to load
        bs = BeautifulSoup(browser.page_source, "lxml")
        browser.quit()
    else:
        print("Either --input or --url should be specified!")
        exit(-1)

    markdownFile = open(args.output, encoding="utf-8", mode="w")
    pageHTML = bs.find("main", class_="page-html")
    contents = pageHTML.contents
    for mainDiv in contents:
        htmlUnparse(mainDiv, markdownFile)
    markdownFile.close()
