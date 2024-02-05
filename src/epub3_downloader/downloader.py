import os
import dataclasses

from bs4 import BeautifulSoup
from readability import Document
import requests

@dataclasses.dataclass
class WebDocument:
    url: str
    title: str
    content: str
    author: str = None

    @classmethod
    def make(self, url:str, data:str=None):
        if not data:
            response = requests.get(url)
            data = response.text

        doc = Document(response.text)
        title = doc.title()
        html_content = doc.summary()
        soup = BeautifulSoup(html_content, 'lxml')

        if not soup.head:
            new_head = soup.new_tag("head")
            soup.html.insert(0, new_head)

        meta_utf8 = soup.new_tag("meta")
        meta_utf8.attrs["charset"] = "utf-8"
        soup.head.insert(0, meta_utf8)

        new_title = soup.new_tag("title")
        new_title.string = title
        soup.head.append(new_title)

        new_h1 = soup.new_tag("h1")
        new_h1.string = title
        soup.body.insert(0, new_h1)

        return WebDocument(
            url=url,
            title=title,
            content=soup.prettify()
        )
    
    def to_ebook(self, output_dir:str="."):
        from ebooklib import epub
        import os
        import re
        import datetime

        # Create a new EPUB book
        book = epub.EpubBook()

        # Set the book title and other metadata
        book.set_title(self.title)
        book.set_language('en')
        # book.add_author('Author Name')

        # Create an EPUB chapter with your HTML content
        chapter = epub.EpubHtml(title=self.title, file_name='webpage.xhtml', lang='en')
        chapter.content = self.content

        # Add chapter to the book
        book.add_item(chapter)

        # Define book spine and table of contents
        book.spine = ['nav', chapter]
        book.toc = [epub.Link('webpage.xhtml', self.title, 'webpage')]

        # Add default NCX and nav files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        ## the filename is YYYY-MM Title, with title stripped of special characters
        today = datetime.date.today()
        yyyy = today.year
        mm = today.month
        scrubbed_title = re.sub(r'[^!%-,_. A-Za-z0-9]+', ' ', self.title)
        scrubbed_title = re.sub(r'\s+', ' ', scrubbed_title).strip()
        output_file = f"{yyyy:04d}-{mm:02d} {scrubbed_title}.epub"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write the EPUB file
        epub.write_epub(os.path.join(output_dir, output_file), book, {})

        print(f"EPUB file has been created: {os.path.join(output_dir, output_file)}")


if __name__ == '__main__':
    wdoc = WebDocument.make("https://www.telegraph.co.uk/business/2024/02/04/tories-must-cut-corporation-tax-beat-labour-election/"
    wdoc.to_ebook()
