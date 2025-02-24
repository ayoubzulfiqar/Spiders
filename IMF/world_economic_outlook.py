import os
import requests


def getURLs() -> list[str]:
    urls: list[str] = []
    for year in range(2020, 2025):
        url = f"https://www.imf.org/-/media/Files/Publications/WEO/WEO-Database/{year}/October/WEOOct{year}all.xls"
        urls.append(url)
    return urls


def download():
    urls: list[str] = getURLs()
    downloadDir: str = "Data"  # Directory to save files
    os.makedirs(downloadDir, exist_ok=True)  # Create directory if it doesn't exist

    for url in urls:
        try:
            print(f"Downloading: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an error for bad status codes (e.g., 404, 500)

            # Extract the year from the URL for the filename
            year = url.split("/")[-3]  # Extract the year from the URL path
            filename = os.path.join(downloadDir, f"WEOOct{year}all.xls")

            # Save the file in binary mode
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Saved: {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")


# TODO:
# - Data Processing & Processing
# - Converting to JSON or CSV
