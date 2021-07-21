"""Extract."""

from gig import ents
from utils import jsonx, tsv

from mobility._constants import MISSING_DSD_NAME_TO_DSD_ID
from mobility._utils import log

REGEX_FILE = r'movement-range-data-(?P<date_str>\d{4}-\d{2}-\d{2}).zip'
DIR_TMP = '/tmp/tmp.mobility'
COVERAGE_LIMIT = 0.1


def _expand_regions(ds_to_dsd_to_info):
    ds_to_region_to_info = {}

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
        ds_to_region_to_info[_ds] = _expand_regions_in_ds(dsd_to_info)
    return ds_to_region_to_info


def _extract_data(lk_text_file):
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

        ds_to_dsd_to_info[_ds][dsd_id] = (float)(
            data['all_day_ratio_single_tile_users']
        )

    ds_to_region_to_info = _expand_regions(ds_to_dsd_to_info)

    data_file_name = '/tmp/mobility.lk-data-%s.json' % ('latest')
    jsonx.write(data_file_name, ds_to_region_to_info)
    log.info('Expanded LK data to %s', (data_file_name))

    return ds_to_region_to_info
