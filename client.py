import asyncio
import struct
import xml.etree.ElementTree

#
# Message format is an unsigned integer in network order that defines the
# length of the payload followed by the binary payload. The data stream is
# a sequence of messages.
# [N] [N bytes]
# [unsigned] [bytes...]
#


class Stream:
    def __init__(self, reader, writer):
        self.__reader = reader
        self.__writer = writer
        self.__name_map = None

    async def read_message(self, timeout=None):
        return await read_message(self.__reader, timeout)

    async def write_message(self, timeout=None):
        return await write_message(self.__writer, timeout)


async def open_connection(host='127.0.0.1', port=32076):
    reader, writer = await asyncio.open_connection(port=32076)

    message = await read_message(reader, 1)
    if not is_metadata(message):
        raise RuntimeError('unknown data stream format')

    return Stream(reader, writer)


async def read_message(reader, timeout=None):
    """Read one message from the Shadow data stream

    Keyword arguments:
    reader -- asyncio.StreamReader connected the Shadow data stream
    timeout -- wait for timeout seconds for the message to arrive, set to None
        to block until the stream read completes

    Returns bytes object
    """
    header = await asyncio.wait_for(reader.readexactly(4), timeout)
    length = int.from_bytes(header, byteorder='big')

    return await asyncio.wait_for(reader.readexactly(length), timeout)


async def write_message(writer, message, timeout=None):
    """Write one message to the Shadow data stream

    writer -- asyncio.StreamWriter connected the Shadow data stream
    message -- bytes to write to the stream
    timeout -- wait for timeout seconds for the message to send, set to None to
        block until the stream write completes
    """
    length = len(message)
    header = int(length).to_bytes(4, byteorder='big')

    writer.write(header)
    writer.write(message)
    await asyncio.wait_for(writer.drain(), timeout)


def is_metadata(message):
    """Returns true iff the Shadow data stream message contains metadata rather
    than a measurement sample
    """
    return message.startswith(b'<?xml')


def parse_metadata(message):
    #
    # Convert a list of channel names to a map from integer key to string name.
    #
    # Parse an XML message string from a MotionSDK.Client stream. The first
    # message is always a flat list of node names and integer key pairs.
    #
    # parse_name_map('<node key="1" id="Name"/>...') -> {1: "Name", ...}
    #
    # Use the key to look up the node name for every sample of measurement data
    # until we receive a new XML message.
    #
    tree = xml.etree.ElementTree.fromstring(message)

    # <node key="N" id="Name"> ... </node>
    items = tree.findall('node')

    return {
        int(item.get('key')): item.get('id')
        for item in items
    }


def unpack_sample(message):
    """Convert a binary message from the Shadow data stream into a Python dict

    message -- bytes from the data stream

    Returns dict object
    """
    #
    # Format of one sample from the configurable data service. All data is
    # little endian and 4 bytes (unsigned, float C types).
    #
    # node =
    #   [key] [N] [N values]
    #   [unsigned] [unsigned] [float, ...]
    #
    # message = [node, ...]
    #
    sample = {}

    i = 0
    while i < len(message):
        (key, length) = struct.unpack_from('<2I', message, i)
        i += 2 * 4

        sample[key] = struct.unpack_from(f'<{length}f', message, i)
        i += length * 4

    return sample
