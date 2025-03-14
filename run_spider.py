from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from img_scraper.spiders.image_spider import ImageSpider
from scrapy.signalmanager import dispatcher
from scrapy import signals

class MyCrawlerProcess(CrawlerProcess):
    def __init__(self, settings=None):
        super().__init__(settings)
        self.item_count = 0
        dispatcher.connect(self.item_scraped, signal=signals.item_scraped)

    def item_scraped(self, item, response, spider):
        self.item_count += 1

# Load project settings
settings = get_project_settings()
process = MyCrawlerProcess(settings)
process.crawl(ImageSpider)
process.start()

print(f"Total items scraped: {process.item_count}")