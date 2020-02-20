from django.shortcuts import render
import requests


def check_update(ncode: str):
    response = requests.post(
        'http://scrapy:6800/schedule.json',
        data={'project': 'narou_scraper', 'spider': 'novel_all_episodes', 'ncode': ncode}
    )
    return response
