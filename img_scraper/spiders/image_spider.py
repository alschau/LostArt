import scrapy
import time
import json
import random
from img_scraper.items import ArtworkItem
from scrapy_splash import SplashRequest



class ImageSpider(scrapy.Spider):
    name = "imagespider"
    start_url = "https://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz/gemaelde-bilder/gemaelde-7048?sfId=c9164799-0d49-498b-8156-35f19381b381&isNavigation=true&page=1&sort=1"

    # --- Lookup Tables for Detail Information ---
    motives = ["Abstrakt", "Comic/Zeichnungen", "Landschaft", "Natur/Pflanzen", "Portraits/Menschen", "Schrift", "Städte/Gebäude", "Tiere", "Andere Motive"]
    techniques = ["Acryl", "Aquarell", "Graphit", "Holzschnitt", "Kohle", "Kupfertisch", "Linoleumschnitt", "Lithographie", "Öl", "Pastell", "Radierung", "Stahltisch", "Tusche", "Andere Techniken"]
    conditions = ["Neu", "Neuwertig", "Gebraucht", "Defekt"]
    handovers = ["Selbstabholung", "Versand", "Selbstabholung, Versand"]

    # --- Variables ---
    nr_of_sites = 5

    # --- List of User Agents ---
    user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
]


    def __init__(self, *args, **kwargs):
        super(ImageSpider, self).__init__(*args, **kwargs)
        self.items_scraped = 0
        self.site_count = 0
        self.site_url = ""


    def start_requests(self):
        self.site_url = self.start_url
        while self.site_count < self.nr_of_sites:
            yield SplashRequest(url=self.site_url, callback=self.parse,
                       headers={"User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list)-1)]})
        
    
    def parse(self, response):
        # --- Get all entries on the search results page ---
        all_entries_on_page = [item['url'] for item in json.loads(response.xpath('//script[@type="application/ld+json"]/text()').get()).get('itemListElement', [])]
        print("This page has "+str(len(all_entries_on_page))+" entries on this page.")

        # --- Only the first entry for now to test the button ---
        # entry_url = response.urljoin(all_entries_on_page[0])
        # yield SplashRequest(url=entry_url, callback=self.parse_product_page)
        
        # --- All entries on the page ---
        for entry in all_entries_on_page:
            entry_url = response.urljoin(entry)
            yield SplashRequest(url=entry_url, callback=self.parse_product_page,
                       headers={"User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list)-1)]})

        self.site_count += 1
        next_page = response.css('a[data-testid="pagination-top-next-button"]::attr(href)').get()
        self.site_url = response.urljoin(next_page)


    def parse_product_page(self, response):
        item = ArtworkItem()
        
        # --- Title ---
        title = response.css('h1[data-testid="ad-detail-header"]::text').get()
        item["title"] = title

        # --- Image URLs ---
        image_url = response.css('img[data-testid^="image-"][alt^="Bild 1 von"]::attr(src)').get()
        absolute_img_url = response.urljoin(image_url)
        item['image_url'] = absolute_img_url

        # --- Price ---
        price = response.css('span[data-testid="contact-box-price-box-price-value"]::text').get()
        item["price"] = price

        # --- Description ---
        description = response.css('div[data-testid="ad-description-Beschreibung"]::text').get()
        item["description"] = description

        # --- Detail Information ---
        detail_information = response.xpath('//div[@data-testid="attribute-value"]/text()').getall()
        if len(detail_information) == 4:
            item['motive'] = detail_information[0]
            item['technique'] = detail_information[1]
            item['condition'] = detail_information[2]
            item['handover'] = detail_information[3]
        else:
            item['motive'] = None
            item['technique'] = None
            item['condition'] = None
            item['handover'] = None
            for detail in detail_information:
                if detail in self.motives:
                    item['motive'] = detail
                elif detail in self.techniques:
                    item['technique'] = detail
                elif detail in self.conditions:
                    item['condition'] = detail
                elif detail in self.handovers:
                    item['handover'] = detail

        # --- This can be done later but I keep the placeholders for now ---
        # item['size'] = None
        # item['artist'] = None
        # item['year'] = None

        # --- yield item and increase the counter ---
        yield item
        self.items_scraped += 1 
