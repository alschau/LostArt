import scrapy
from scrapy.pipelines.images import ImagesPipeline

class CustomImagesPipeline(ImagesPipeline):
    def process_item(self, item, spider):
        # print("Pipeline aufgerufen:", item)  # Debugging
        return super().process_item(item, spider)
    
