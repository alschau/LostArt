from scrapy.item import Item, Field

class ArtworkItem(Item):
    title = Field()
    image_url = Field()
    price = Field()
    description = Field()
    motive = Field()
    technique = Field()
    condition = Field()
    handover = Field()

    # size = Field()
    # artist = Field()
    # year = Field()

