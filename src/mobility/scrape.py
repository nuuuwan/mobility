"""Implements mobility."""

import os
import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from utils import timex
from utils.cache import cache

from mobility._constants import CACHE_NAME, CACHE_TIMEOUT
from mobility._utils import log

URL_HDX_MOBILITY = 'https://data.humdata.org/dataset/movement-range-maps?'
REGEX_FILE = r'movement-range-data-(?P<date_str>\d{4}-\d{2}-\d{2}).zip'


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


def scrape():
    """Scrape data."""
    download_url = get_download_url()
    zip_file = os.path.split(download_url)[-1]
    re_result = re.match(REGEX_FILE, zip_file)
    if re_result:
        date_str = re_result.groupdict()['date_str']
        unixtime = timex.parse_time(date_str, '%Y-%m-%d')
        date_id = timex.format_time(unixtime, '%Y%m%d')
    else:
        log.error('Invalid zip file: %s', zip_file)
        return
    log.info('Downloading data for %s', date_str)

    tmp_dir = '/tmp/mobility.%s' % (date_id)
    os.system('wget -P %s %s' % (tmp_dir, download_url))
    log.info('Downloaded data from %s to %s', download_url, tmp_dir)

    log.info('Downloaded data to %s', zip_file)
    os.system('unzip -d %s -o %s' % (
        tmp_dir,
        os.path.join(tmp_dir, zip_file)),
    )
    log.info('Unzipped data')

    lk_text_file = '/tmp/mobility.lk-data-%s.txt' % (date_id)
    text_file = '%s/movement-range-%s.txt' % (tmp_dir, date_str)
    os.system('head -n 1 %s > %s' % (
        text_file,
        lk_text_file,
    ))
    os.system('grep LKA %s >> %s' % (
        text_file,
        lk_text_file,
    ))
    log.info('Extracted LK data to %s', lk_text_file)

    os.system('rm -rf %s' % tmp_dir)
    log.info('Removed %s' % tmp_dir)
