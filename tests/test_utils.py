from Tracker.utils import validUsername


def test_notfound_pbinfo():
    assert validUsername("Tedyst123", "pbinfo") is False


def test_notfound_infoarena():
    assert validUsername("Tedyst123", "infoarena") is False


def test_notfound_codeforces():
    assert validUsername("Tedyst123", "codeforces") is False


def test_pbinfo():
    assert validUsername("Tedyst", "pbinfo") is True


def test_infoarena():
    assert validUsername("Tedyst", "infoarena") is True


def test_codeforces():
    assert validUsername("Tedyst", "codeforces") is True