import json
import logging
import os
import time
from pathlib import Path

from decorator import decorator


log = logging.getLogger(__name__)


def _cache_hit(fname, ttl):
    if val := os.environ.get("DIVVYNOCACHE"):
        log.debug("ignoring cache because DIVVYNOCACHE=%s", val)
        return False
    if not os.path.isfile(fname):
        log.debug("cache doesn't exist at %s", fname)
        return False
    mtime = os.stat(fname).st_mtime
    cache_age = int(time.time() - mtime)
    if cache_age > ttl:
        log.debug("ignoring cache because too old (%ds)", cache_age)
        return False
    log.debug("cache hit @ %s", fname)
    return True


@decorator
def filesystem_cache(func, fname="memo.json", ttl=3600, *args, **kwargs):
    if _cache_hit(fname, ttl):
        return json.loads(Path(fname).read_text())
    result = func(*args, **kwargs)
    serialized = json.dumps(result)
    log.debug("caching result to %s (%d bytes)", fname, len(serialized))
    Path(fname).write_text(serialized)
    return result
