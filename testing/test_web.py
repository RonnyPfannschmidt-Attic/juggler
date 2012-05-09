

def test_web(ghost):
    res, items = ghost.open('/')
    assert res.http_status == 200

