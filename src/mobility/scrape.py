"""Implements mobility."""

import os
import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from utils import tsv, jsonx
from utils.cache import cache

from gig import ents

from mobility._constants import CACHE_NAME, CACHE_TIMEOUT, URL_HDX_MOBILITY
from mobility._utils import log

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


def _download_zip(download_url):
    zip_file = '/tmp/tmp.mobility.zip'
    os.system('wget %s -O %s ' % (download_url, zip_file))
    log.info(
        'Downloaded zip from %s to %s',
        download_url,
        zip_file,
    )
    return zip_file


def _unzip(zip_file):
    os.system('unzip -d %s -o %s' % (
        DIR_TMP,
        zip_file,
    ))
    log.info('Unzipped %s to %s', zip_file, DIR_TMP)


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


def _expand_regions(ds_to_dsd_to_info):
    dsd_to_region_to_info = {}

    dsd_index = ents.get_entity_index('dsd')
    district_index = ents.get_entity_index('district')
    province_index = ents.get_entity_index('province')
    country_index = ents.get_entity_index('country')

    def _expand_regions_in_ds(dsd_to_info):
        region_to_info = {}
        region_to_immo_pop = {}
        region_to_data_pop = {}
        for dsd_id, info in dsd_to_info.items():
            region_to_info[dsd_id] = info

            dsd_ent = dsd_index[dsd_id]
            dsd_pop = dsd_ent['population']

            for region_id in [
                dsd_ent['district_id'],
                dsd_ent['province_id'],
                'LK',
            ]:
                if region_id not in region_to_immo_pop:
                    region_to_immo_pop[region_id] = 0
                    region_to_data_pop[region_id] = 0
                region_to_immo_pop[region_id] += dsd_pop * info
                region_to_data_pop[region_id] += dsd_pop

        for region_id in region_to_immo_pop:
            immo_pop = region_to_immo_pop[region_id]
            data_pop = region_to_data_pop[region_id]

            if len(region_id) == 5:
                region_ent = district_index[region_id]
            elif len(region_id) == 4:
                region_ent = province_index[region_id]
            else:
                region_ent = country_index[region_id]

            region_pop = region_ent['population']
            coverage = data_pop / region_pop
            if coverage < COVERAGE_LIMIT:
                continue
            region_to_info[region_id] = immo_pop / data_pop

        return region_to_info

    for _ds, dsd_to_info in ds_to_dsd_to_info.items():
        dsd_to_region_to_info[_ds] = _expand_regions_in_ds(dsd_to_info)
    return dsd_to_region_to_info


def _extract_data(lk_text_file, date_str):
    data_list = tsv.read(lk_text_file)
    ds_to_dsd_to_info = {}

    dsd_name_to_dsd_id = {}

    def _get_dsd_id(dsd_name):
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

        return dsd_name_to_dsd_id[dsd_name]

    for data in data_list:
        dsd_name = data['polygon_name']
        dsd_id = _get_dsd_id(dsd_name)
        if not dsd_id:
            continue

        _ds = data['ds']
        if _ds not in ds_to_dsd_to_info:
            ds_to_dsd_to_info[_ds] = {}

        ds_to_dsd_to_info[_ds][dsd_id] = \
            (float)(data['all_day_ratio_single_tile_users'])

    dsd_to_region_to_info = _expand_regions(ds_to_dsd_to_info)

    data_file_name = '/tmp/mobility.lk-data-%s.json' % (date_str)
    jsonx.write(data_file_name, dsd_to_region_to_info)
    log.info('Expanded LK data to %s', (data_file_name))

    latest_data_file_name = '/tmp/mobility.lk-data-%s.json' % ('latest')
    os.system('cp %s %s' % (data_file_name, latest_data_file_name))
    log.info('Copied LK data to %s', (latest_data_file_name))


def scrape():
    """Scrape data."""
    download_url = get_download_url()
    zip_file = _download_zip(download_url)
    _unzip(zip_file)

    date_str = _get_date_str(download_url)
    lk_text_file = _extract_lk_text(date_str)
    _extract_data(lk_text_file, date_str)
