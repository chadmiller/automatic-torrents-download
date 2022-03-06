import logging as loggingmod

logger = loggingmod.getLogger(__name__)


def based_on(have):
    to_do = set(have)
    while to_do:
        show, season, ep = to_do.pop()
        for candidate in [next_ep_this_season(show, season, ep), next_ep_next_season(show, season, ep)]:
            if candidate not in have:
                found = yield candidate  # send up for processing, receive if it was found

                if found:
                    logger.info("Candidate %s was enqueued for downloading so adding its nexts to consideration list.", candidate)
                    to_do.add(candidate)


def next_ep_this_season(show, season, ep):
    return (show, season, ep+1)


def next_ep_next_season(show, season, _):
    return (show, season+1, 1)
