import os
import re
import bs4
import pandas as pd

class DirectoryPreparer:
    '''Class for sorting message files in right order'''

    def __init__(self, directory: str):
        '''
        Parameters
        ----------
        directory : str
            A directory with and exported data from Telegram
        '''
        self._directory = directory

    def get_message_files(self):
        '''Function that return sorted file names'''
        def atoi(text: str):
            return int(text) if text.isdigit() else text

        def natural_keys(text):
            return [atoi(c) for c in re.split(r'(\d+)', text)]

        def add_directory_to_filename(file):
            return os.path.join(self._directory, file)

        files = [add_directory_to_filename(item)
                 for item in os.listdir(self._directory)
                 if re.match("messages\d*\.html", item)]
        first_file = add_directory_to_filename('messages.html')
        files.remove(first_file)
        files.sort(key=natural_keys)
        files.insert(0, first_file)

        return files


class Parser:
    def __init__(self, encoding='utf8'):
        self._encoding = encoding
        self._previous_author = ''
        self._data = []
        self._chat_name = None

    @property
    def data(self):
        return self._data

    @property
    def chat_name(self):
        return self._chat_name

    def _parse_timestamp(self, div):
        """
        Parse a timestamp from message
        """
        return div.select("div.body div.pull_right")[0].get('title')

    def _parse_author(self, div):
        """
        Parse an author from message
        """
        try:
            author = div.select("div.from_name")[0].get_text().strip()
        except IndexError:
            author = self._previous_author
        self._previous_author = author
        return author

    def _parse_message(self, div):
        """
        Parse an one div with message
        """

        def forwarded_content(div):
            """
            If message was forwarded return content in that message
            """
            forwarded = None
            try:
                forwarded = div.select("div.forwarded div.text")[
                    0].get_text().strip()
            except IndexError:
                pass

            try:
                forwarded = div.select("div.forwarded div.media_wrap a")[0].get('href')
            except IndexError:
                pass

            return forwarded

        def normal_content(div):
            """
            If message wasn't return content in that message
            """
            normal = None
            try:
                normal = div.select("div.text")[0].get_text().strip()
            except IndexError:
                pass

            try:
                normal = div.select("div.media_wrap a")[0].get('href')
            except IndexError:
                pass

            return normal

        content = normal_content(div) if not None else forwarded_content(div)
        return content

    def _parse_chat_name(self, soup):
        name = soup.find('div', class_="text bold").get_text().strip()
        return name

    def _parse_page(self, soup: bs4.BeautifulSoup):
        """
        Method for parse one page
        """
        message_divs = soup.find_all('div',
                                     id=re.compile("message"),
                                     class_=re.compile("message default clearfix.*"))
        for div in message_divs:
            timestamp = self._parse_timestamp(div)
            author = self._parse_author(div)
            message = self._parse_message(div)
            self._data.append([timestamp, author, message])

        if self._chat_name is None:
            self._chat_name = self._parse_chat_name(soup)

    def parse(self, file):
        with open(file, 'r', encoding=self._encoding) as f:
            soup = bs4.BeautifulSoup(f, 'html5lib')
            self._parse_page(soup)

        return self.data

    def to_dataframe(self):
        headers = ['timestamp', 'author', 'message']
        df = pd.DataFrame(data=self.data, columns=headers)
        return df
