#!/usr/bin/python3

import os
import re
import logging

logger = logging.getLogger(__name__)


def scan(root):
    # discover what we have on disk
    have = set()
    for _, _, filenames in os.walk(root):
        for filename in filenames:
            match = re.match(r"^(.*?) \(s(\d\d)e(\d\d)-(\d\d)\)", filename)
            if match:
                have.add((match.group(1), int(match.group(2)), int(match.group(3))))
            else:
                match = re.match(r"^(.*?) \(s(\d\d)e(\d\d)\)", filename)
                if match:
                    have.add((match.group(1), int(match.group(2)), int(match.group(3))))
                else:
                    pass
    return have
