import yaml

import logging
import logging.config
from pathlib import Path


ROOT = Path(__file__).parent.parent


# TODO hard coded path
path = ROOT / "conf" / "logging.yaml"
with path.open(mode="r") as fd:
    config = yaml.load(fd, Loader=yaml.FullLoader)

logging.config.dictConfig(config)
log = logging.getLogger(__name__)
log.info("! initialized logging")

# make sure state is initialized right after logging init
from rui_be import state  # noqa: F401, E402
from rui_be import changelog  # noqa: F401, E402
