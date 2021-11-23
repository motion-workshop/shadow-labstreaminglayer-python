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
import client

import asyncio
import unittest


async def asyncio_test_client(ctx):
    reader, writer = await asyncio.open_connection(port=32076)

    message = await client.read_message(reader)

    message = b'<?xml version="1.0"?><configurable><Lq/></configurable>'

    await client.write_message(writer, message)

    for i in range(10):
        message = await client.read_message(reader)
        if client.is_metadata(message):
            name_map = client.parse_metadata(message)
            ctx.assertIsInstance(name_map, dict)
            continue

        sample = client.unpack_sample(message)
        ctx.assertIsInstance(sample, dict)
        for item in sample.values():
            ctx.assertEqual(len(item), 4)


async def asyncio_test_stream(ctx):
    stream = await client.open_connection()

    message = b'<?xml version="1.0"?><configurable><Bq/><c/></configurable>'

    await stream.write_message(message)

    message = await stream.read_message()
    sample = client.unpack_sample(message)
    ctx.assertIsInstance(sample, dict)

    name_map = stream.get_name_map()
    ctx.assertIsInstance(name_map, dict)

    for item in sample.values():
        ctx.assertEqual(len(item), 8)

    for i in range(10):
        message = await stream.read_message()

        sample = client.unpack_sample(message)
        for item in sample.values():
            ctx.assertEqual(len(item), 8)


class TestClient(unittest.TestCase):

    def test_client(self):
        asyncio.run(asyncio_test_client(self))

    def test_stream(self):
        asyncio.run(asyncio_test_stream(self))

    def test_parse_metadata(self):
        xml_string = \
            '<?xml version="1.0"?>' \
            '<node key="0" id="default">' \
            '<node key="1" id="FirstName"></node>' \
            '<node key="9" id="LastName"/>' \
            '</node>'

        name_map = client.parse_metadata(xml_string)

        self.assertIsInstance(name_map, dict)

        for k, v in name_map.items():
            self.assertIsInstance(k, int)
            self.assertIsInstance(v, str)

        self.assertNotIn(0, name_map)
        self.assertIn(1, name_map)
        self.assertIn(9, name_map)

        self.assertEqual(name_map.get(1), 'FirstName')
        self.assertEqual(name_map.get(9), 'LastName')

    def test_is_metadata(self):
        self.assertTrue(client.is_metadata(b'<?xml version="1.0"?><node/>'))
        self.assertFalse(client.is_metadata(b'<node/>'))


if __name__ == '__main__':
    unittest.main()
