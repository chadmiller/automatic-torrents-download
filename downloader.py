import subprocess
import logging

from random import randint
from datetime import datetime, timedelta
from tpblite import TPB
import sqlite3

logger = logging.getLogger(__name__)

def get_best(term):
    site = TPB()
    results = site.search(term)
    best = results.getBestTorrent(min_seeds=30, min_filesize='800 MiB', max_filesize='4 GiB')
    if best:
        return best.magnetlink
    raise IndexError((term, site))


def enqueue_all(want):
    db = sqlite3.connect("torrent-queuer-state.sqlite3")
    cursor = db.cursor()

    try:
        cursor.execute("""
            create table if not exists cache (
                subject text,
                last_try datetime,
                fail_count integer
            )
        """)

        now = datetime.utcnow()
        for name, season, ep in sorted(want):
            subject = "{} s{:02d}e{:02d}".format(name, season, ep)

            row = cursor.execute("select last_try, fail_count from cache where subject = ?", (subject,)).fetchone()
            if row:
                last_try = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                fail_count = int(row[1])
                next_allowed = last_try + timedelta(days=min(2**fail_count, randint(90, 120)))

                if now < next_allowed:
                    logger.info("not trying to get %r for now. maybe in %s", subject, next_allowed)
                    continue
                else:
                    logger.debug("%r is allowed as it's only been tried %s times", subject, fail_count)
            else:
                logger.debug("I have no memory of %r", subject)

            try:
                good_torrent_magnet = get_best(subject)

                if good_torrent_magnet:
                    enqueue_magnet_link(good_torrent_magnet)

                cursor.execute("delete from cache where subject = ?", (subject,))
            except IndexError:
                logger.warning("wanted %s but none was found", subject)
                if row:
                    cursor.execute("update cache set fail_count=fail_count+1, last_try=? where subject = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), subject,))
                else:
                    cursor.execute("insert into cache (fail_count, last_try, subject) values (1, ?, ?)", (now.strftime("%Y-%m-%d %H:%M:%S"), subject,))
        db.commit()
    finally:
        db.close()


def enqueue_magnet_link(magnet_link, subject):
    logging.info("Enqueuing %r from %s", subject, magnet_link)
    assert magnet_link.startswith("magnet:"), magnet_link
    subprocess.run(["transmission-remote", "--add", magnet_link], stdout=subprocess.DEVNULL, timeout=10, check=True)


def list_in_progress():
    have = set()
    # discover what we are already downloading
    with subprocess.Popen(["transmission-remote", "--list"], stdout=subprocess.PIPE) as p:
        for n, line in enumerate(p.stdout):
            if n == 0: continue  # skip header

            name = line.decode("UTF-8").rstrip()[70:]
            have.add(name)

    return have
