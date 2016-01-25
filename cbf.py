
import numpy
import hashlib
import base64
import collections
import cbf_c  # TODO need to be renamed
import struct
import re

header_base = '''_array_data.data\r
;\r
--CIF-BINARY-FORMAT-SECTION--\r
Content-Type: application/octet-stream;\r
     conversions="x-CBF_BYTE_OFFSET"\r
Content-Transfer-Encoding: BINARY\r
X-Binary-Size: {binary_size:d}\r
X-Binary-ID: 1\r
X-Binary-Element-Type: "{element_type}"\r
X-Binary-Element-Byte-Order: LITTLE_ENDIAN\r
Content-MD5: {md5_hash}\r
X-Binary-Number-of-Elements: {number_of_elements:d}\r
X-Binary-Size-Fastest-Dimension: {size_fastest_dimension:d}\r
X-Binary-Size-Second-Dimension: {size_second_dimension:d}\r
X-Binary-Size-Padding: 4095\r
\r\n'''

header_end_mark = b'\x0C\x1A\x04\xD5'


def write(filename, data, header=None):
    """
    Write CBF file
    :param filename: Filename of cbf file to write
    :param data: Data to write to cbf file (numpy array)
    :param header: Custom header to write to file
    :return: Compressed size
    """

    # Check input data
    if data.itemsize == 4:
        element_type = 'signed 32-bit integer'
    elif data.itemsize == 2:
        element_type = 'signed 16-bit integer'
    else:
        raise TypeError(str(data.dtype))

    # Compress data
    output_buffer = compress(data)

    md5_hash = base64.b64encode(hashlib.md5(output_buffer).digest())

    # Write file
    file_handle = open(filename, 'wb')
    # file_handle.write(header['version'])
    # file_handle.write(header['convention'])
    # file_handle.write(header['contents'])
    file_handle.write(header_base.format(binary_size=output_buffer.size, number_of_elements=data.size, size_fastest_dimension=data.shape[1], size_second_dimension=data.shape[0], md5_hash=md5_hash, element_type=element_type))
    file_handle.write(header_end_mark)
    file_handle.write(output_buffer)
    file_handle.close()


def read(filename, metadata=True):
    """
    Read CBF files
    :param filename: Name of the file to read
    :param metadata: Return metadata alongside with the data
    :return: Data (namedtuple('data', 'metadata')), if metadata=False metadata is None
    """

    file_descriptor = open(filename, 'rb')
    file_content = file_descriptor.read()
    file_descriptor.close()

    # Find text/binary delimiter
    header_end_index = file_content.find(header_end_mark)

    # Read header
    file_header = file_content[:header_end_index]
    pattern = re.compile(r'X-Binary-([\w-]*)([\s:]*)(.*)')
    header = dict()
    for line in file_header.decode().splitlines():
        m = pattern.search(line)
        if m:
            key = m.group(1).lower().replace('-', '_')  # Sanitize key names
            val = m.group(3).strip()
            try:
                val = int(val)
            except ValueError:
                try:
                    val = float(val)
                except ValueError:
                    val = val
            header[key] = val
    # print(header)

    # Read binary data
    input_buffer = file_content[header_end_index + len(header_end_mark):]

    # Uncompress data
    data_type = numpy.uint32 if '32' in header['element_type'] else numpy.uint16
    data = uncompress(input_buffer, header['size_second_dimension'], header['size_fastest_dimension'], data_type)

    # Declaration data class / named tuple
    data_tuple = collections.namedtuple('Data', 'data metadata')

    return data_tuple(data, header)


def compress(data):
    """
    Compress data
    :param data: Data to compress (numpy array)
    :return: Compressed data (numpy array - uint8-c-order)
    """
    output_buffer = numpy.ndarray(data.nbytes, dtype=numpy.uint8, order='C')
    compressed_size = cbf_c.compress(data, output_buffer)
    # print(compressed_size)
    return output_buffer[:compressed_size]


def uncompress(binary_data, size_x, size_y, data_type):
    """
    Uncompress data
    :param binary_data: Compressed binary data
    :return: Uncompressed data (numpy array)
    """

    size = size_x * size_y * data_type(0).nbytes

    output_buffer = b'a' * size
    cbf_c.uncompress(binary_data, output_buffer)
    numpy_array = numpy.fromstring(output_buffer, dtype=data_type)
    numpy_array = numpy_array.reshape(size_x, size_y)
    return numpy_array
