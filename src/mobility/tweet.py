"""Tweet."""

import argparse
import tweepy

from utils import timex

from mobility._utils import log
from mobility.plot import _plot_all


def _tweet(
    twtr_api_key,
    twtr_api_secret_key,
    twtr_access_token,
    twtr_access_token_secret,
):
    plot_info = _plot_all()

    tweet_text = '''
Mobility Report {_ds}

% of Sri Lankans "Staying Put", according to @Facebook's mobility data.

#lka #SriLanka #COVID19SL #LockDown @HumanData
    '''.format(
        _ds=plot_info['ds'],
    )

    log.info('Tweeting: %s', tweet_text)
    log.info('Tweet Length: %d', len(tweet_text))

    image_files = plot_info['image_files']
    log.info('Status images: %s', ';'.join(image_files))

    if not twtr_api_key:
        return

    auth = tweepy.OAuthHandler(twtr_api_key, twtr_api_secret_key)
    auth.set_access_token(twtr_access_token, twtr_access_token_secret)
    api = tweepy.API(auth)

    media_ids = []
    for image_file in image_files:
        res = api.media_upload(image_file)
        media_id = res.media_id
        media_ids.append(media_id)
        log.info('Uploaded image %s to twitter as %s', image_file, media_id)

    log.info(api.update_status(tweet_text, media_ids=media_ids))

    date = timex.format_time(timex.get_unixtime(), '%B %d, %Y %H:%M%p')
    timezone = timex.get_timezone()
    log.info(api.update_profile(
        description='''Statistics about Sri Lanka.

Automatically updated at {date} {timezone}
        '''.format(date=date, timezone=timezone)
    ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run pipeline for custom_dgigovlk_covid19.',
    )
    for twtr_arg_name in [
        'twtr_api_key',
        'twtr_api_secret_key',
        'twtr_access_token',
        'twtr_access_token_secret',
    ]:
        parser.add_argument(
            '--' + twtr_arg_name,
            type=str,
            required=False,
            default=None,
        )
    args = parser.parse_args()
    _tweet(
        args.twtr_api_key,
        args.twtr_api_secret_key,
        args.twtr_access_token,
        args.twtr_access_token_secret,
    )
