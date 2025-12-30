import re
import yaml
from pathlib import Path
from .models import StationConfig
from .config import station_rules_file


class MetadataParser:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        self.stations = {
            name: StationConfig(**cfg) 
            for name, cfg in raw_config['stations'].items()
        }
    
    def parse(self, station_name: str, live_desc: str):
        if station_name not in self.stations:
            return 'Station Rule Not defined', None
        
        config = self.stations[station_name]
        
        # Check skip conditions
        for skip_pattern in config.skip_if_contains:
            if skip_pattern in live_desc:
                return None, None
        
        # Apply parser strategy
        if config.parser_type == "delimiter_split":
            return self._parse_delimiter(live_desc, config)
        elif config.parser_type == "regex_match":
            return self._parse_regex(live_desc, config)
        
        return None, None
    
    def _parse_delimiter(self, live_desc: str, config: StationConfig):
        if config.delimiter not in live_desc:
            return None, None
        
        parts = live_desc.split(config.delimiter, 1)
        if len(parts) != 2:
            return None, None
        
        if config.artist_first:
            return parts[0].strip(), parts[1].strip()
        else:
            return parts[1].strip(), parts[0].strip()
    
    def _parse_regex(self, live_desc: str, config: StationConfig):
        match = re.match(config.pattern, live_desc)
        if not match:
            return None, None
        
        groups = match.groups()
        # Map to artist, title based on field_mapping
        mapping = {field: groups[i] for i, field in enumerate(config.field_mapping)}
        return mapping.get('artist'), mapping.get('title')

try:
    parser = MetadataParser(station_rules_file)
except FileNotFoundError:
    parser = MetadataParser(Path(Path.cwd() / "sample-data" / "sample-station_rules.yaml"))
except Exception as e:
    raise e