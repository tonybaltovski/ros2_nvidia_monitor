"""Smoke tests for the nvidia_monitor package."""


def test_import():
    """The package and its node module import without error."""
    import nvidia_monitor  # noqa: F401
    from nvidia_monitor import nvidia_monitor_node  # noqa: F401


def test_main_callable():
    """The console-script entry point exposes a callable main()."""
    from nvidia_monitor.nvidia_monitor_node import main

    assert callable(main)
