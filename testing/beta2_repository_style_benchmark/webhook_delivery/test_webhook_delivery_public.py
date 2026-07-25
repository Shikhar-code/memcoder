from webhook_delivery import build_delivery


try:
    build_delivery({})
except ValueError as error:
    assert str(error) == "endpoint_name is required"
else:
    raise AssertionError("Missing endpoint_name should raise ValueError")

assert build_delivery({"endpoint_name": " billing-events ", "timeout_seconds": 10}) == {
    "endpoint_name": "billing-events",
    "timeout_seconds": 10,
}

print("PASS: public webhook delivery validation")
