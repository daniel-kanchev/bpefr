import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bpefr.items import Article


class BpefrSpider(scrapy.Spider):
    name = 'bpefr'
    start_urls = ['https://www.bpe.fr/banque-privee/public/web/pm_7278/tous-les-articles']

    def parse(self, response):
        links = response.xpath('//div[@class="magHomeArticle "]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="dateDetailArticle"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="wysiwyg bpearticleblog"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
