"""Render summary."""

from utils import filex

from mobility._utils import log


def _render_readme(ds_to_region_to_info):
    ds_list = list(ds_to_region_to_info.keys())
    n_ds = len(ds_list)
    ds_min, ds_max = ds_list[0], ds_list[-1]

    readme_file_name = '/tmp/README.md'
    filex.write(
        readme_file_name,
        '''# Facebook Movement Range Maps

This GitHub Repository contains data for {n_ds} days from {ds_min} to {ds_max}.

## Appendix: Original Data Source

Source: https://data.humdata.org/dataset/movement-range-maps

> This data includes movement changes measured by Facebook throughout March,
April, May, and June 2020 starting from a baseline in February. Data is
provided in one global tab-delimited text file.

In this GitHub Repository, the data for Sri Lanka (LKA) has been extracted,
normalized (by adding ISO codes for DSDs), and also expanded to provinces,
districts, and the entire country.

        '''.format(
            n_ds=n_ds,
            ds_min=ds_min,
            ds_max=ds_max,
        ),
    )
    log.info("Rendered summary to %s", readme_file_name)
