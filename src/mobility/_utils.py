"""Utils."""

import os
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('mobility')


def _download_zip(download_url, zip_file):
    os.system('wget %s -O %s ' % (download_url, zip_file))
    log.info(
        'Downloaded zip from %s to %s',
        download_url,
        zip_file,
    )


def _unzip(zip_file, unzip_dir):
    os.system('unzip -d %s -o %s' % (
        unzip_dir,
        zip_file,
    ))
    log.info('Unzipped %s to %s', zip_file, unzip_dir)
