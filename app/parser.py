from urllib import error, request
from bs4 import BeautifulSoup
from pywebcopy import save_webpage
from itertools import chain
import os


download_folder = "{}/app/sites".format(os.getcwd())


class Parser:
    def __init__(self, web_url, depth, task_id):
        self.web_url = web_url
        self.depth = depth
        self.task_id = task_id

    def save_page(self, url):
        kwargs = {
            "zip_project_folder": False,
            "bypass_robots": True
        }
        project_folder = "{}/{}".format(download_folder, self.task_id)
        if not os.path.exists(project_folder):
            os.mkdir(project_folder)

        return save_webpage(
            url=url,
            project_folder=project_folder,
            **kwargs
        )

    @staticmethod
    def get_links(soup, url):
        links = soup("a")
        final_links = []
        for link in links:
            if "href" not in link.attrs:
                continue

            if "http" in link["href"] or "#" in link["href"]:
                continue

            full_url = request.urljoin(url, link["href"])

            if full_url[0:4] == "http":
                final_links.append(full_url)
        return final_links

    def load_page(self, url):
        try:
            page = request.urlopen(url)
        except error.URLError:
            raise Exception("Website {} not responding".format(url))
        except Exception as e:
            print("Error while page loading\n{}".format(e))
            return []
        try:
            self.save_page(url)
        except Exception as e:
            print("Error while page saving\n{}".format(e))
        soup = BeautifulSoup(page.read(), "html.parser")
        return self.get_links(soup, url)

    def parse(self):
        urls = [self.web_url]
        indexed_urls = []
        temp_urls = []
        for i in range(self.depth):
            for url in urls:
                if url in indexed_urls:
                    continue
                indexed_urls.append(url)
                try:
                    links = self.load_page(url)
                except Exception as e:
                    if len(urls) == 1:
                        raise Exception("No sites were loaded")
                    else:
                        continue
                temp_urls = list(set(chain(indexed_urls, links)))
            urls = temp_urls
        return urls