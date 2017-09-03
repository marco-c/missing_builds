from datetime import datetime, timedelta
import requests


def get_nightly_version():
    r = requests.get('https://product-details.mozilla.org/1.0/firefox_versions.json')
    return r.json()['FIREFOX_NIGHTLY']


def get_latest_nightly_buildID(version):
    r = requests.get('https://archive.mozilla.org/pub/mobile/nightly/latest-mozilla-central-android-api-16/fennec-' + version + '.multi.android-arm_info.txt')
    return r.text[len('buildID='):-1]


def parse_buildID(buildID):
    buildID = str(buildID)
    return datetime(
        int(buildID[:4]),
        int(buildID[4:6]),
        int(buildID[6:8]),
        int(buildID[8:10]),
        int(buildID[10:12]),
        int(buildID[12:14])
    )


def get_socorro_buildIDs(version):
    r = requests.get('https://crash-stats.mozilla.com/api/SuperSearch/', params={
        'product': 'FennecAndroid',
        'version': version,
        '_results_number': 0,
        '_facets': 'build_id',
    })
    return [elem['term'] for elem in r.json()['facets']['build_id']]


if __name__ == '__main__':
    version = get_nightly_version()

    latest_nightly = get_latest_nightly_buildID(version)
    date = parse_buildID(latest_nightly)

    if date < datetime.utcnow() - timedelta(2):
        delta = abs(date - datetime.utcnow())
        raise Exception('Build missing for ' + str(delta.days) + ' days!')

    socorro_buildIDs = get_socorro_buildIDs(version)
    if latest_nightly[:8] not in [str(bid)[:8] for bid in socorro_buildIDs]:
        raise Exception('Crash reports missing for latest Nightly (' + latest_nightly + ')! Latest buildID on Socorro: ' + str(max(socorro_buildIDs)))

    print('Latest build ' + str(latest_nightly))
    print('Latest build on Socorro: ' + str(max(socorro_buildIDs)))
