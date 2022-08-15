# Importing Beautiful soup and xlsxwriter
from bs4 import BeautifulSoup
import xlsxwriter
import requests
import re
import json

# A function to generate excel file


def generate_excel(workbook_name: str, worksheet_name: str, headers_list: list, data: list):
    # Creating workbook
    workbook = xlsxwriter.Workbook(workbook_name)
    # Creating worksheet
    worksheet = workbook.add_worksheet(worksheet_name)
    # Adding data
    for index1, entry in enumerate(data):
        for index2, header in enumerate(headers_list):
            worksheet.write(index1+1, index2, entry[header])
    # Fixing Headers
    worksheet.write(0, 0, headers_list[0])
    worksheet.write(0, 1, headers_list[1])
    worksheet.write(0, 2, headers_list[2])
    worksheet.write(0, 3, headers_list[3])
    # Close workbook
    workbook.close()


# getting the search key word
search_key = input("What do you wnat to search?\n").replace(" ", "+")
url = f"https://www.youtube.com/results?search_query={search_key}"

response = requests.get(url).text
soup = BeautifulSoup(response, 'lxml')

script = soup.find_all("script")[33]

json_text = re.search('var ytInitialData = (.+)[,;]{1}', str(script)).group(1)
json_data = json.loads(json_text)

content = (
    json_data
    ['contents']['twoColumnSearchResultsRenderer']
    ['primaryContents']['sectionListRenderer']
    ['contents'][0]['itemSectionRenderer']['contents']
)

all_channels = [{
    "Channel_name": "DNF",
    "Video_title": "DNF",
    "Subscribers": 0,
    "Channel_link": "DNF"
} for video in range(22)]

video_counter = 0

for data in content[:100]:
    for key, value in data.items():
        if type(value) is dict:
            if "didYouMean" in key:
                continue
            print(video_counter)
            for k, v in value.items():
                if k == "title":
                    if ("runs" in v):
                        video_title = v['runs'][0]['text']
                        all_channels[video_counter]['Video_title'] = video_title
                elif k == "longBylineText":
                    if ("runs" in v):
                        channel_name = v['runs'][0]['text']
                        all_channels[video_counter]['Channel_name'] = channel_name
                        channel_url = (
                            "https://www.youtube.com/" + v['runs'][0]['navigationEndpoint']['browseEndpoint']['canonicalBaseUrl'])
                        all_channels[video_counter]['Channel_link'] = channel_url

                    _response = requests.get(channel_url).text
                    _soup = BeautifulSoup(_response, "lxml")
                    _script = str(_soup.find_all("script")[33])

                    JSON_START = int(_script.find("ytInitialData") + 16)
                    JSON_END = -10
                    _script = _script[JSON_START:JSON_END]
                    _script = json.loads(_script)

                    _subcount = (
                        _script
                        ['header']['c4TabbedHeaderRenderer']['subscriberCountText']['simpleText']
                    )
                    all_channels[video_counter]['Subscribers'] = str(
                        _subcount).replace("subscribers", "").strip()

            # counting videos
            video_counter += 1
# creating the excel file
generate_excel(f"{search_key.replace('+','_')}.xlsx", "firstsheet",
               ["Channel_name", "Video_title", "Subscribers", "Channel_link"], all_channels)
