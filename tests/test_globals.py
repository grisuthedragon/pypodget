import pypodget.globals as g


def test_verbose_default_true():
    g.__verbose__ = True
    assert g.verbose() is True


def test_set_verbose_false():
    g.set_verbose(False)
    assert g.verbose() is False


def test_set_verbose_true():
    g.set_verbose(True)
    assert g.verbose() is True


def test_set_verbose_idempotent():
    g.set_verbose(True)
    g.set_verbose(True)
    assert g.verbose() is True


def test_verbose_isolation():
    g.set_verbose(False)
    assert g.verbose() is False
    g.set_verbose(True)
    assert g.verbose() is True


def test_set_verbose_none():
    g.set_verbose(None)
    assert g.verbose() is None
