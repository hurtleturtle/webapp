from bs4 import BeautifulSoup


def get_soup(filepath):
    with open(filepath, 'r') as f:
        return BeautifulSoup(f, features='lxml')


def get_chapters(soup, container):
    # unsafe_tags = {'script', 'link', 'a'}
    # unsafe_tag_selector = ', '.join(unsafe_tags)
    # unsafe_elements = soup.select(unsafe_tag_selector)
    #
    # for el in unsafe_elements:
    #     el.decompose()

    return soup.select(container)


def get_heading(chapter, selector):
    return chapter.select_one(selector).string.strip('\n').strip()
