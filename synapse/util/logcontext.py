#
# This file is licensed under the Affero General Public License (AGPL) version 3.
#
# Copyright (C) 2023 New Vector, Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# See the GNU Affero General Public License for more details:
# <https://www.gnu.org/licenses/agpl-3.0.html>.
#
# Originally licensed under the Apache License, Version 2.0:
# <http://www.apache.org/licenses/LICENSE-2.0>.
#
# [This file includes modifications made by New Vector Limited]
#
#

"""
Backwards compatibility re-exports of ``synapse.logging.context`` functionality.
"""

from synapse.logging.context import (
    LoggingContext,
    LoggingContextFilter,
    PreserveLoggingContext,
    defer_to_thread,
    make_deferred_yieldable,
    nested_logging_context,
    preserve_fn,
    run_in_background,
)

__all__ = [
    "defer_to_thread",
    "LoggingContext",
    "LoggingContextFilter",
    "make_deferred_yieldable",
    "nested_logging_context",
    "preserve_fn",
    "PreserveLoggingContext",
    "run_in_background",
]
