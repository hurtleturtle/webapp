from bs4 import BeautifulSoup


def get_soup(filepath):
    with open(filepath, 'r') as f:
        return BeautifulSoup(f, features='lxml')


def get_chapters(soup, container):
    return soup.select(container)


def get_heading(chapter, selector):
    return chapter.select_one(selector).string.strip('\n').strip()
