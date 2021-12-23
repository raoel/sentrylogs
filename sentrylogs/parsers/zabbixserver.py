

from datetime import datetime, timezone
import re

from . import Parser

class Zabbixserver(Parser):
    """Zabbix server logs"""

    def __init__(self, filepath):
        super().__init__(filepath)
        self.pattern = re.compile(
        r"^\s*\d+\:(\d{4})(\d{2})(\d{2})\:(\d{2})(\d{2})(\d{2}).(\d{3})\s*([^$]*)", re.M
    )

    def parse(self, line) -> bool:
        line_matches = self.pattern.match(line)
        if not line_matches:
            return False

        year, month, day, hour, minutes, seconds, microseconds, logline = line_matches.groups()
        line_timestamp = datetime(int(year),
                              int(month),
                              int(day),
                              int(hour),
                              int(minutes),
                              int(seconds),
                              int(microseconds), tzinfo=timezone.utc)
        self.message = logline
        self.level = 'error'
        self.data['datetime'] = line_timestamp.isoformat()
        return True
