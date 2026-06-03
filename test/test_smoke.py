# Copyright 2026 Tony Baltovski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Smoke tests for the nvidia_monitor package."""


def test_import():
    """The package and its node module import without error."""
    import nvidia_monitor  # noqa: F401
    from nvidia_monitor import nvidia_monitor_node  # noqa: F401


def test_main_callable():
    """The console-script entry point exposes a callable main()."""
    from nvidia_monitor.nvidia_monitor_node import main

    assert callable(main)
