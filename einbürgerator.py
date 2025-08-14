from http import HTTPStatus
import argparse
import logging
import random
import subprocess
import sys
import time
import tempfile
from urllib3.util.retry import Retry

import requests
import requests.adapters

SERVICES = {
    'leben-in-deutschland': '351180',
    'trade-driving-license-3rd-countries': '327537'
}

NO_APPOINTMENTS = 'Leider sind aktuell keine Termine'


def get_main_page_url(service_code):
    return f'https://service.berlin.de/terminvereinbarung/termin/all/{service_code}/'


def get_refresh_page_url(service_code):
    return f'https://service.berlin.de/terminvereinbarung/termin/restart/?providerList=122626%2C122659%2C122664%2C122666%2C122671%2C325853%2C325987%2C351435%2C351438%2C351444%2C351636&requestList={service_code}'


def refresh_page(service_code):
    session = requests.Session()
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=Retry(
        total=5,
        status_forcelist=[500, 502, 503, 504],
        backoff_factor=1
    )))

    main_page_url = get_main_page_url(service_code)
    # The User-Agent spoofing to Google Chrome doesn't work: berlin.de detects it and returns 403 status code consistently.
    session.headers.update({'User-Agent': "Einbuergerator/1.0"})
    resp = session.get(main_page_url)
    yield resp
    while True:
        resp = session.get(main_page_url)
        yield resp


def main():
    parser = argparse.ArgumentParser(
        description='Monitor Berlin VHS for available appointments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Available services:
  leben-in-deutschland              Einbürgerungstest (citizenship test) - default
  trade-driving-license-3rd-countries  Trade driving license from 3rd countries

Examples:
  python einbürgerator.py
  python einbürgerator.py --service trade-driving-license-3rd-countries'''
    )
    parser.add_argument(
        '--service', '-s',
        choices=list(SERVICES.keys()),
        default='leben-in-deutschland',
        help='Service to monitor for appointments (default: %(default)s)'
    )

    args = parser.parse_args()
    service_code = SERVICES[args.service]

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s : %(levelname)s : %(message)s'
    )
    logger = logging.getLogger('default')
    logger.info('Monitoring service: %s (code: %s)', args.service, service_code)

    total, failures = 0, 0
    main_page_url = get_main_page_url(service_code)
    try:
        for resp in refresh_page(service_code):
            total += 1
            next_sleep = random.uniform(60, 90)
            if resp.status_code != HTTPStatus.OK:
                failures += 1
                logger.warning('HTTP status %d, waiting for %0.1f seconds', resp.status_code, next_sleep)
            elif NO_APPOINTMENTS in resp.text:
                logger.info(f'"{NO_APPOINTMENTS}", waiting for %0.1f seconds', next_sleep)
            else:
                logger.info('The appointment is probably available.')
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
                    temp_file.write(resp.content)
                logger.info("See the page here: %s", temp_file.name)
                logger.info("Opening the page in the browser and exiting.")
                subprocess.run(["open", main_page_url])
                break
            time.sleep(next_sleep)
    except KeyboardInterrupt:
        print(" (interrupted by the user)")

    logger.info('Share of failed requests: %0.0f%%', 100 * failures / total)

    return 0

if __name__ == '__main__':
    sys.exit(main())
