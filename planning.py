def based_on(have):
    want = set()
    for show, season, ep in have:
        want.add(next_ep_this_season(show, season, ep))
        want.add(next_ep_next_season(show, season, ep))
    return want


def next_ep_this_season(show, season, ep):
    return (show, season, ep+1)


def next_ep_next_season(show, season, _):
    return (show, season+1, 1)
