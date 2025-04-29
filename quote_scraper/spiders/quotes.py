import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com/"]

    def parse(self, response):
        # Extract quotes from the current page
        quotes = response.css("div.quote")
        for quote in quotes:
            # Extract quote text, author, and tags
            quote_text = quote.css("span.text::text").get()
            author = quote.css("small.author::text").get()
            tags = quote.css("div.tags a.tag::text").getall()

            # Yield the extracted data as an item
            yield {
                "quote": quote_text,
                "author": author,
                "tags": ", ".join(tags) if tags else "N/A"
            }

        # Handle pagination: Find the "Next" link and follow it
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            # Follow the next page link and call parse again
            yield response.follow(next_page, callback=self.parse)
