import requests
import zipfile
import os
import csv

# File paths
zip_filename = "population.zip"
extracted_folder = "population_data"  # Folder for extracted files
filename = ""  # CSV filename


def download():
    global filename
    source = "http://api.worldbank.org/countries/all/indicators/SP.POP.TOTL?downloadformat=csv"

    # Download the ZIP file
    response = requests.get(source, timeout=3000.0)
    with open(zip_filename, "wb") as d:
        d.write(response.content)

    # Extract files into the current directory
    os.makedirs(extracted_folder, exist_ok=True)
    with zipfile.ZipFile(zip_filename, "r") as zip_ref:
        zip_ref.extractall(extracted_folder)

    # Find the correct CSV file
    for path in os.scandir(extracted_folder):
        if path.is_file() and path.name.startswith("API_SP.POP.TOTL_DS2_EN"):
            filename = os.path.join(extracted_folder, path.name)
            break  # Stop after finding the correct file


def process():
    global filename
    if not filename:
        raise FileNotFoundError(
            "No valid CSV file found. Ensure `download()` runs successfully."
        )

    with open(filename, "r", newline="", encoding="utf-8") as fo:
        lines = list(csv.reader(fo))

    headings = lines[4]  # Get column headers
    lines = lines[5:]  # Data starts from row 5

    outheadings = ["Country Name", "Country Code", "Year", "Value"]
    outlines = []

    for row in lines:
        for idx, year in enumerate(headings[4:]):  # Iterate over years
            if row[idx + 4]:  # Ensure value is not empty
                value = row[idx + 4]
                outlines.append(row[:2] + [int(year), value])

    # Ensure output directory exists
    os.makedirs("data", exist_ok=True)

    # Save the processed data
    with open("data/population.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(outheadings)
        writer.writerows(outlines)


if __name__ == "__main__":
    download()
    process()
