from http import HTTPStatus
import logging
import random
import subprocess
import sys
import time
import tempfile
from urllib3.util.retry import Retry

import requests
import requests.adapters

MAIN_PAGE = 'https://service.berlin.de/terminvereinbarung/termin/all/351180/'
REFRESH_PAGE = 'https://service.berlin.de/terminvereinbarung/termin/restart/?providerList=122626%2C122659%2C122664%2C122666%2C122671%2C325853%2C325987%2C351435%2C351438%2C351444%2C351636&requestList=351180'
NO_APPOINTMENTS = 'Leider sind aktuell keine Termine'


def refresh_page():
    session = requests.Session()
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=Retry(
        total=5,
        status_forcelist=[500, 502, 503, 504],
        backoff_factor=1
    )))

    # The User-Agent spoofing to Google Chrome doesn't work: berlin.de detects it and returns 403 status code consistently.
    # session.headers.update({'User-Agent': "Einbuergerator/1.0"})
    resp = session.get(MAIN_PAGE)
    yield resp
    while True:
        resp = session.get(MAIN_PAGE)
        yield resp


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s : %(levelname)s : %(message)s'
    )
    logger = logging.getLogger('default')

    total, failures = 0, 0
    try:
        for resp in refresh_page():
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
                subprocess.run(["open", MAIN_PAGE])
                break
            time.sleep(next_sleep)
    except KeyboardInterrupt:
        print(" (interrupted by the user)")

    logger.info('Share of failed requests: %0.0f%%', 100 * failures / total)

    return 0

if __name__ == '__main__':
    sys.exit(main())
