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


async def asyncio_test_client():
    reader, writer = await asyncio.open_connection(port=32076)

    message = await client.read_message(reader)

    print(message)

    message = b'<?xml version="1.0"?><configurable><Lq/><c/></configurable>'

    await client.write_message(writer, message)

    for i in range(10):
        message = await client.read_message(reader)
        if client.is_metadata(message):
            name_map = client.parse_metadata(message)
            print(name_map)
            continue

        print(len(message))

        sample = client.unpack_sample(message)
        print(sample)


async def asyncio_test_stream():
    stream = await client.open_connection()

    message = b'<?xml version="1.0"?><configurable><Lq/><c/></configurable>'

    await stream.write_message(message)

    for i in range(10):
        message = await stream.read_message()
        print(len(message))

        sample = client.unpack_sample(message)
        print(sample)


class TestClient(unittest.TestCase):

    # def test_client(self):
    #     asyncio.run(asyncio_test_client())

    def test_stream(self):
        asyncio.run(asyncio_test_stream())


if __name__ == '__main__':
    unittest.main()
