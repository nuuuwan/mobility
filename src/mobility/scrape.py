"""Implements mobility."""

import os
import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from utils import timex, tsv, jsonx
from utils.cache import cache

from gig import ents

from mobility._constants import CACHE_NAME, CACHE_TIMEOUT
from mobility._utils import log

URL_HDX_MOBILITY = 'https://data.humdata.org/dataset/movement-range-maps?'
REGEX_FILE = r'movement-range-data-(?P<date_str>\d{4}-\d{2}-\d{2}).zip'
MISSING_DSD_NAME_TO_DSD_ID = {
        'K.F.G. & G. Korale': 'LK-2130',
        'Panduwasnuwara': 'LK-6145',
        'N. Palatha Central': 'LK-7115',
        'N. Palatha East': 'LK-7133',
        'Arachchikattuwa PS': 'LK-6230',
        'Dehiwala-Mount Lavinia': 'LK-1130',
        'Hanwella': 'LK-1115',
        'Valikamam East': 'LK-4118',
        'Valikamam North': 'LK-4112',
        'Valikamam South': 'LK-4115',
        'Valikamam South-West': 'LK-4109',
        'Valikamam West': 'LK-4106',
        'Thenmaradchy (Chavakachcheri)': 'LK-4130',
        'Vadamaradchi South-West': 'LK-4121',
        'Vadamaradchy North': 'LK-4127',
}


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

    temp_dir = '/tmp/temp.mobility.%s' % (date_id)
    os.system('wget -P %s %s' % (temp_dir, download_url))
    log.info('Downloaded data from %s to %s', download_url, temp_dir)

    log.info('Downloaded data to %s', zip_file)
    os.system('unzip -d %s -o %s' % (
        temp_dir,
        os.path.join(temp_dir, zip_file)),
    )
    log.info('Unzipped data')

    lk_text_file = '%s/mobility.lk-data-%s.txt' % (temp_dir, date_id)
    text_file = '%s/movement-range-%s.txt' % (temp_dir, date_str)
    os.system('head -n 1 %s > %s' % (
        text_file,
        lk_text_file,
    ))
    os.system('grep LKA %s >> %s' % (
        text_file,
        lk_text_file,
    ))
    log.info('Extracted LK data to %s', (lk_text_file))

    data_list = tsv.read(lk_text_file)
    dsd_name_to_dsd_id = {}
    ds_to_dsd_to_info = {}

    for data in data_list:
        dsd_name = data['polygon_name']
        if dsd_name not in dsd_name_to_dsd_id:
            if dsd_name in MISSING_DSD_NAME_TO_DSD_ID:
                dsd_id = MISSING_DSD_NAME_TO_DSD_ID[dsd_name]
                dsd_name_to_dsd_id[dsd_name] = dsd_id
            else:
                dsds = ents.get_entities_by_name_fuzzy(
                    dsd_name,
                    limit=1,
                    filter_entity_type='dsd',
                )
                if len(dsds) > 0:
                    dsd = dsds[0]
                    dsd_id = dsd['dsd_id']
                    dsd_name_to_dsd_id[dsd_name] = dsd_id
                else:
                    log.error('Could not find DSD for %s', dsd_name)
                    dsd_name_to_dsd_id[dsd_name] = None

        dsd_id = dsd_name_to_dsd_id[dsd_name]
        if not dsd_id:
            continue
        ds = data['ds']
        if ds not in ds_to_dsd_to_info:
            ds_to_dsd_to_info[ds] = {}

        # all_day_ratio_single_tile_users:
        #   Positive proportion of users staying put within a single location
        ds_to_dsd_to_info[ds][dsd_id] = \
            (float)(data['all_day_ratio_single_tile_users'])
    data_file_name = '/tmp/mobility.lk-data-%s.json' % (date_id)
    jsonx.write(data_file_name, ds_to_dsd_to_info)
    log.info('Expanded LK data to %s', (data_file_name))

    latest_data_file_name = '/tmp/mobility.lk-data-%s.json' % ('latest')
    os.system('cp %s %s' % (data_file_name, latest_data_file_name))
    log.info('Copied LK data to %s', (latest_data_file_name))
