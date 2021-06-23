"""Uploaded data  to data branch."""

from mobility import scrape, extract, summary


if __name__ == '__main__':
    lk_text_file = scrape.scrape()
    ds_to_region_to_info = extract._extract_data(lk_text_file)
    summary._render_readme(ds_to_region_to_info)
