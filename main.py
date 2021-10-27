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
import pylsl

import argparse
import asyncio
import sys

#
# For each node in the Shadow devkit stream copy these channels. Use the
# node.id ("Body", "Hips", "LeftThigh", etc) as the marker name for MoCap
# meta-data as per XDF specs.
#
# https://github.com/sccn/xdf/wiki/MoCap-Meta-Data
#
# (<marker>.label, type, unit)
#
CHANNEL_INFO = (
    ('Lqw', 'OrientationA', 'quaternion'),
    ('Lqx', 'OrientationB', 'quaternion'),
    ('Lqy', 'OrientationC', 'quaternion'),
    ('Lqz', 'OrientationD', 'quaternion'),
    ('cw', 'Confidence', 'normalized'),
    ('cx', 'PositionX', 'centimeters'),
    ('cy', 'PositionY', 'centimeters'),
    ('cz', 'PositionZ', 'centimeters')
)


async def open_shadow_stream(args):
    #
    # Connect to the devkit data stream running in the Shadow app. Request the
    # channels we want to read in this application and return the client
    # ready to stream sample data.
    #
    stream = await client.open_connection(host=args.host, port=args.port)

    #
    # Request the channels that we want from every connected device. The full
    # list is available here:
    #
    #   https://www.motionshadow.com/download/media/configurable.xml
    #
    # Select the local quaternion (Lq) and positional constraint (c)
    # channels here. 8 numbers per device per frame. Ask for inactive nodes
    # which are not necessarily attached to a sensor but are animated as part
    # of the Shadow skeleton.
    #
    channels = ''.join([
        f'<{item[0]}/>'
        for item in CHANNEL_INFO
    ])

    message = \
        '<?xml version="1.0"?>' \
        '<configurable inactive="1">' \
        f'{channels}' \
        '</configurable>'

    await stream.write_message(message.encode())

    return stream


def open_stream_outlet(args, name_map, container):
    #
    # Create a LSL Stream Outlet based our channels and the first current input
    # sample from our Shadow devkit client.
    #
    num_channel = len(container) * len(CHANNEL_INFO)

    info = pylsl.StreamInfo(
        'ShadowMocap',
        'MoCap',
        num_channel,
        100,
        'float32',
        'fe69d558-2c31-4730-84a3-ea411d37a141')

    if args.header:
        channels = info.desc().append_child('channels')
        acquisition = info.desc().append_child('acquisition')
        markers = info.desc().append_child('markers')

        for key, item in container.items():
            if key not in name_map:
                raise RuntimeError(
                    'device missing from name map, unable to create header')

            if len(CHANNEL_INFO) != len(item):
                raise RuntimeError(
                    f'expected {len(CHANNEL_INFO)} channels but found '
                    '{len(item)}, unable to create header')

            node_name = name_map.get(key)
            for channel_name, channel_type, channel_unit in CHANNEL_INFO:
                label = f'{node_name}.{channel_name}'

                channel = channels.append_child('channel')
                channel.append_child_value('label', label)
                channel.append_child_value('marker', node_name)
                channel.append_child_value('type', channel_type)
                channel.append_child_value('unit', channel_unit)

            marker = markers.append_child('marker')
            marker.append_child_value('label', node_name)

        acquisition.append_child_value('manufacturer', 'Motion Workshop')
        acquisition.append_child_value('model', 'Shadow')

    return pylsl.StreamOutlet(info, max_buffered=1)


async def shadow_to_labstreaminglayer(args):
    #
    # Open input stream connection from the Shadow app.
    #
    stream = await open_shadow_stream(args)

    #
    # Wait for first sample. This will also load the current name map.
    #
    message = await stream.read_message(5)
    container = client.unpack_sample(message)
    name_map = stream.get_name_map()

    #
    # Open output stream.
    #
    outlet = open_stream_outlet(args, name_map, container)

    while True:
        # Wait for the next sample.
        message = await stream.read_message(1)
        container = client.unpack_sample(message)

        #
        # Make a flat list of all of the values that are part of one sample.
        #
        sample = [
            value
            for key, item in container.items()
            for value in item
        ]

        outlet.push_sample(sample)


def main(argv):
    parser = argparse.ArgumentParser(
        description=(
            'Read data from your Shadow mocap system and create a Stream'
            ' Outlet for the Lab Streaming Layer (LSL)'))

    parser.add_argument(
        '--header',
        help='write header to the stream as per the XDF metadata spec',
        action='store_true')
    parser.add_argument(
        '--host',
        help='IP address of your Shadow app',
        default='127.0.0.1')
    parser.add_argument(
        '--port',
        help='port number of your Shadow app',
        type=int,
        default=32076)

    args = parser.parse_args()

    asyncio.run(shadow_to_labstreaminglayer(args))


if __name__ == '__main__':
    main(sys.argv[1:])
