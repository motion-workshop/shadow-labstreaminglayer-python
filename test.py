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
import client

import unittest


class TestMain(unittest.TestCase):

    def test_parse_name_map(self):
        xml_string = \
            '<?xml version="1.0"?>' \
            '<node key="0" id="default">' \
            '<node key="1" id="FirstName"></node>' \
            '<node key="9" id="LastName"/>' \
            '</node>'

        name_map = main.parse_name_map(xml_string)

        self.assertIsInstance(name_map, dict)

        for k, v in name_map.items():
            self.assertIsInstance(k, int)
            self.assertIsInstance(v, str)

        self.assertNotIn(0, name_map)
        self.assertIn(1, name_map)
        self.assertIn(9, name_map)

        self.assertEqual(name_map.get(1), 'FirstName')
        self.assertEqual(name_map.get(9), 'LastName')

    def test_make_shadow_client(self):
        # Create a mock argparse result
        args = type('obj', (object,), {'host': '', 'port': 32076})

        client = main.make_shadow_client(args)

        self.assertIsInstance(client, object)

    def test_make_stream_outlet(self):
        # Create a mock argparse result
        args = type('obj', (object,), {'header': True})

        xml_string = \
            '<?xml version="1.0"?>' \
            '<node key="0" id="default">' \
            '<node key="1" id="FirstName"></node>' \
            '<node key="9" id="LastName"/>' \
            '</node>'

        container = {
            1: (float(0),) * len(main.CHANNEL_INFO),
            9: (float(1),) * len(main.CHANNEL_INFO)
        }

        outlet = main.make_stream_outlet(args, xml_string, container)

        self.assertIsInstance(outlet, object)


if __name__ == '__main__':
    unittest.main()
