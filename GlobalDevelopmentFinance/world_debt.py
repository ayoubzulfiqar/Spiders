import json
import scrapy
from scrapy.crawler import CrawlerProcess
import os
import requests


URL = "https://www.worldbank.org/en/programs/debt-statistics/idr/products"


class TableSpider(scrapy.Spider):
    name = "table_spider"
    start_urls = [URL]  # Replace with the actual URL

    def parse(self, response):
        data_dict = {}

        # Locate table rows
        rows = response.xpath("//table//tr")

        for row in rows:
            title = row.xpath(
                ".//td[1]/text()"
            ).get()  # Extract year from the first column
            links = row.xpath(".//td[2]//a")

            # Extract all links as a list of (Month, URL) tuples
            link_list = {
                link.xpath("text()").get().strip(): response.urljoin(
                    link.xpath("@href").get()
                )
                for link in links
                if link.xpath("text()").get()
            }

            if title and link_list:
                data_dict[title.strip()] = link_list  # Store as {Year: {Month: URL}}

        # Save data to JSON file
        with open(
            "GlobalDevelopmentFinance/world_debt_links.json", "w", encoding="utf-8"
        ) as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=4)

        print("Data saved to output.json")  # Confirmation message


# Run the spider without a Scrapy project
process = CrawlerProcess(settings={"LOG_LEVEL": "ERROR"})
process.crawl(TableSpider)
process.start()


def download(jsonFile, downloadFolder="GlobalDevelopmentFinance/data"):
    # Create the download folder if it doesn't exist
    os.makedirs(downloadFolder, exist_ok=True)

    # Load JSON data
    with open(jsonFile, "r", encoding="utf-8") as f:
        data = json.load(f)

    for year, links in data.items():
        for month, url in links.items():
            try:
                print(f"Downloading: {year} - {month} from {url}")

                # Get the filename from the URL
                filename = url.split("/")[-1]
                filePath = os.path.join(downloadFolder, filename)

                # Send HTTP GET request
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raise an error for failed requests

                # Save the file
                with open(filePath, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)

                print(f"✔ Downloaded: {filePath}")

            except requests.RequestException as e:
                print(f"❌ Failed to download {url}: {e}")


# Call the function with the JSON file
download("GlobalDevelopmentFinance/world_debts_links.json")
