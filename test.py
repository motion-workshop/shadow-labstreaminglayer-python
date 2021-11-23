#
# Copyright (c) 2021, Motion Workshop
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS'
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
import main

import asyncio
import unittest


async def asyncio_test_outlet(ctx, args):
    client = await main.open_shadow_stream(args)

    ctx.assertIsInstance(client, object)


class TestMain(unittest.TestCase):

    def test_open_shadow_stream(self):
        # Create a mock argparse result
        args = type('obj', (object,), {'host': '', 'port': 32076})
        asyncio.run(asyncio_test_outlet(self, args))

    def test_open_stream_outlet(self):
        # Create a mock argparse result
        args = type('obj', (object,), {'header': True})

        # Mock name mapping
        name_map = {
            1: 'FirstName',
            9: 'LastName'
        }

        # And mock first frame of data
        container = {
            1: (float(0),) * len(main.CHANNEL_INFO),
            9: (float(1),) * len(main.CHANNEL_INFO)
        }

        outlet = main.open_stream_outlet(args, name_map, container)

        self.assertIsInstance(outlet, object)


if __name__ == '__main__':
    unittest.main()
