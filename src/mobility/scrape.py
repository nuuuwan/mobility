"""Scrape."""

import os
import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from utils.cache import cache

from mobility._constants import \
    CACHE_NAME, CACHE_TIMEOUT, \
    URL_HDX_MOBILITY

from mobility._utils import log, _download_zip, _unzip

REGEX_FILE = r'movement-range-data-(?P<date_str>\d{4}-\d{2}-\d{2}).zip'
DIR_TMP = '/tmp/tmp.mobility'
COVERAGE_LIMIT = 0.1


@cache(CACHE_NAME, CACHE_TIMEOUT)
def get_download_url():
    """Get download URL."""
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    browser.get(URL_HDX_MOBILITY)

    links = browser.find_elements_by_xpath(
        "//div[@class='hdx-btn-group hdx-btn-group-fixed']/a",
    )
    download_url = None
    for link in links:
        href = link.get_attribute('href')
        if 'download/movement-range-data' in href:
            download_url = href
            break
    browser.quit()
    log.info('Found download url: %s', download_url)
    return download_url


def _get_date_str(download_url):
    remote_zip_file = os.path.split(download_url)[-1]
    re_result = re.match(REGEX_FILE, remote_zip_file)
    if not re_result:
        log.error('Invalid remote zip file: %s', remote_zip_file)
        return None

    date_str = re_result.groupdict()['date_str']
    return date_str


def _extract_lk_text(date_str):
    text_file = '%s/movement-range-%s.txt' % (DIR_TMP, date_str)
    lk_text_file = '%s/lk-data-%s.txt' % (DIR_TMP, date_str)
    os.system('head -n 1 %s > %s' % (
        text_file,
        lk_text_file,
    ))
    os.system('grep LKA %s >> %s' % (
        text_file,
        lk_text_file,
    ))
    log.info('Extracted LK data from %s to %s', text_file, lk_text_file)
    return lk_text_file


def scrape():
    """Scrape data."""
    download_url = get_download_url()
    zip_file = '/tmp/tmp.mobility.zip'
    _download_zip(download_url, zip_file)
    _unzip(zip_file, DIR_TMP)

    date_str = _get_date_str(download_url)
    lk_text_file = _extract_lk_text(date_str)
    return lk_text_file
