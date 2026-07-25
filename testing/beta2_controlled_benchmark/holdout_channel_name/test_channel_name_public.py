from channel_name import configure_channel


try:
    configure_channel({})
except ValueError as error:
    assert str(error) == "channel_name is required"
else:
    raise AssertionError("Expected missing channel_name validation failure")

assert configure_channel({"channel_name": " alerts "})["channel_name"] == "alerts"
print("PASS: public channel name validation")
