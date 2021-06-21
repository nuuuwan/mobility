"""Implements lk_data."""
import os

from utils import www
from utils.cache import cache

from mobility._constants import CACHE_NAME, CACHE_TIMEOUT


URL_LK_DATA = os.path.join(
    'https://raw.githubusercontent.com/nuuuwan/mobility/data/',
    'mobility.lk-data-latest.json',
)


@cache(CACHE_NAME, CACHE_TIMEOUT)
def get_lk_data():
    """Implement lk_data."""
    ds_to_dsd_to_info = www.read_json(URL_LK_DATA)
    return ds_to_dsd_to_info


@cache(CACHE_NAME, CACHE_TIMEOUT)
def get_ds_list():
    """Get list of dates for which mobility data exists."""
    return list(get_lk_data().keys())


@cache(CACHE_NAME, CACHE_TIMEOUT)
def get_latest_ds():
    """Get latest date for which mobility data exists."""
    return get_ds_list()[-1]


if __name__ == '__main__':
    print(get_latest_ds())
