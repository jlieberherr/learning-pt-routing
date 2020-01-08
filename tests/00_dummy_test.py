from scripts.hello import return_five


def test_return_five():
    print(return_five())
    assert return_five() == 5