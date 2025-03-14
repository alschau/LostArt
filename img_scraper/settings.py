import os

BOT_NAME = 'img_scraper'  # Add a bot name

SPIDER_MODULES = ['img_scraper.spiders']  # Important: Tell Scrapy where your spiders are
NEWSPIDER_MODULE = 'img_scraper.spiders'
# ROBOTSTXT_OBEY = True

# Middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # Disable the default
    'img_scraper.middlewares.RandomUserAgentMiddleware': 400,          # Enable yours
}

# Splash Setup
SPLASH_URL = "http://localhost:8050"
DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
}
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
REQUEST_FINGERPRINTER_CLASS = 'scrapy_splash.SplashRequestFingerprinter'

# Enable the Images Pipeline
ITEM_PIPELINES = {
    'img_scraper.pipelines.CustomImagesPipeline': 300,
}

# Configure the image storage path (relative to project root)
IMAGES_STORE = os.path.join(os.getcwd(), 'images')

# Optional: Add a user agent to be polite
# USER_AGENT = 'My Image Scraper for a University Project'

# Optional: Control download delay (be respectful of the website)
DOWNLOAD_DELAY = 5  # Seconds
RANDOMIZE_DOWNLOAD_DELAY = True

FEEDS = {
    'artworks.json': {  # Output filename
        'format': 'json',  # Output format (json, jsonlines, csv, xml, etc.)
        'encoding': 'utf-8', # Important for handling special characters
        'indent': 4,       # Optional: Pretty-print JSON with 4-space indentation
        'overwrite': True, # Overwrite the file if it exists. Use False to append.
    },
    'artworks.csv': {
        'format': 'csv',
        'fields': ['title', 'price', 'image_urls', 'description'], # Specify the order of columns (optional)
        'encoding': 'utf-8',
        'overwrite': True
    }
}

ROTATING_PROXY_LIST = [
    "213.143.113.82:80",
    "3.127.121.101:80",
    "23.88.116.40:80"
]