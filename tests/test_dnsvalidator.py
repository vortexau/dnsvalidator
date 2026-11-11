"""Regression tests for dnsvalidator input handling."""
import requests

from dnsvalidator.lib.core.input import InputHelper, InputParser


def test_explicit_target_skips_default_list_fetch(monkeypatch):
    def _no_network(*args, **kwargs):
        raise AssertionError("must not touch the network when -t is given")

    monkeypatch.setattr(requests, "get", _no_network)
    args = InputParser().parse(["-t", "127.0.0.1"])
    assert InputHelper.return_targets(args) == {"127.0.0.1"}
