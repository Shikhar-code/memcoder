import importlib
import sys
from pathlib import Path


sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
configure_channel = importlib.import_module("channel_name").configure_channel
for config in ({"channel_name": None}, {"channel_name": "\n"}, {"channel_name": []}):
    try:
        configure_channel(config)
    except ValueError as error:
        assert str(error) == "channel_name is required"
    else:
        raise AssertionError("Hidden channel_name case should raise ValueError")
print("PASS: hidden channel name verification")
