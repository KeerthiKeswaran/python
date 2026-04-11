from minitest.core import test, parameterize, skip

@parameterize("product_id,qty", [(1, 1), (2, 5), (99, 0)])
def test_add_item(product_id, qty):
    assert product_id > 0
    assert qty >= 0

@skip("skipped: no API key")
def test_checkout_stripe():
    pass

def test_full_integration():
    import time
    time.sleep(0.2) # Simulate slow test
    assert True
