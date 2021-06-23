"""Uploaded data  to data branch."""

from mobility import scrape, extract


if __name__ == '__main__':
    lk_text_file = scrape.scrape()
    extract._extract_data(lk_text_file)
