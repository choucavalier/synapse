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
from typing import NoReturn
from unittest.mock import Mock

from twisted.internet import defer
from twisted.internet.defer import Deferred

from synapse.util.caches.cached_call import CachedCall, RetryOnExceptionCachedCall

from tests.test_utils import get_awaitable_result
from tests.unittest import TestCase


class CachedCallTestCase(TestCase):
    def test_get(self) -> None:
        """
        Happy-path test case: makes a couple of calls and makes sure they behave
        correctly
        """
        d: "Deferred[int]" = Deferred()

        async def f() -> int:
            return await d

        slow_call = Mock(side_effect=f)

        cached_call = CachedCall(slow_call)

        # the mock should not yet have been called
        slow_call.assert_not_called()

        # now fire off a couple of calls
        completed_results = []

        async def r() -> None:
            res = await cached_call.get()
            completed_results.append(res)

        r1 = defer.ensureDeferred(r())
        r2 = defer.ensureDeferred(r())

        # neither result should be complete yet
        self.assertNoResult(r1)
        self.assertNoResult(r2)

        # and the mock should have been called *once*, with no params
        slow_call.assert_called_once_with()

        # allow the deferred to complete, which should complete both the pending results
        d.callback(123)
        self.assertEqual(completed_results, [123, 123])
        self.successResultOf(r1)
        self.successResultOf(r2)

        # another call to the getter should complete immediately
        slow_call.reset_mock()
        r3 = get_awaitable_result(cached_call.get())
        self.assertEqual(r3, 123)
        slow_call.assert_not_called()

    def test_fast_call(self) -> None:
        """
        Test the behaviour when the underlying function completes immediately
        """

        async def f() -> int:
            return 12

        fast_call = Mock(side_effect=f)
        cached_call = CachedCall(fast_call)

        # the mock should not yet have been called
        fast_call.assert_not_called()

        # run the call a couple of times, which should complete immediately
        self.assertEqual(get_awaitable_result(cached_call.get()), 12)
        self.assertEqual(get_awaitable_result(cached_call.get()), 12)

        # the mock should have been called once
        fast_call.assert_called_once_with()


class RetryOnExceptionCachedCallTestCase(TestCase):
    def test_get(self) -> None:
        # set up the RetryOnExceptionCachedCall around a function which will fail
        # (after a while)
        d: "Deferred[int]" = Deferred()

        async def f1() -> NoReturn:
            await d
            raise ValueError("moo")

        slow_call = Mock(side_effect=f1)
        cached_call = RetryOnExceptionCachedCall(slow_call)

        # the mock should not yet have been called
        slow_call.assert_not_called()

        # now fire off a couple of calls
        completed_results = []

        async def r() -> None:
            try:
                await cached_call.get()
            except Exception as e1:
                completed_results.append(e1)

        r1 = defer.ensureDeferred(r())
        r2 = defer.ensureDeferred(r())

        # neither result should be complete yet
        self.assertNoResult(r1)
        self.assertNoResult(r2)

        # and the mock should have been called *once*, with no params
        slow_call.assert_called_once_with()

        # complete the deferred, which should make the pending calls fail
        d.callback(0)
        self.assertEqual(len(completed_results), 2)
        for e in completed_results:
            self.assertIsInstance(e, ValueError)
            self.assertEqual(e.args, ("moo",))

        # reset the mock to return a successful result, and make another pair of calls
        # to the getter
        d = Deferred()

        async def f2() -> int:
            return await d

        slow_call.reset_mock()
        slow_call.side_effect = f2
        r3 = defer.ensureDeferred(cached_call.get())
        r4 = defer.ensureDeferred(cached_call.get())

        self.assertNoResult(r3)
        self.assertNoResult(r4)
        slow_call.assert_called_once_with()

        # let that call complete, and check the results
        d.callback(123)
        self.assertEqual(self.successResultOf(r3), 123)
        self.assertEqual(self.successResultOf(r4), 123)

        # and now more calls to the getter should complete immediately
        slow_call.reset_mock()
        self.assertEqual(get_awaitable_result(cached_call.get()), 123)
        slow_call.assert_not_called()
