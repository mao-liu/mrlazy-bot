import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] [%(thread)d:%(threadName)s] %(message)s %(extra)s'
)