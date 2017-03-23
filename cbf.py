
import numpy
import hashlib
import base64
import collections
import cbf_c
import re

miniheader_re = re.compile(
    b'(.*^data_(?P<prefix>.*?)_\d+\r\n)?'
    b'(.*^# Detector: (?P<detector_model>[^,]+),\s*(?P<detector_number>[^,\r\n]+))?'
    b'(.*^# Pixel_size (?P<x_pixel_size>[^ m]+) m x (?P<y_pixel_size>[^ m]+))?'
    b'(.*^# Silicon sensor, thickness (?P<sensor_thickness>[^ ]+))?'
    b'(.*^# Exposure_time (?P<exposure_time>.+?) s\r\n)?'
    b'(.*^# Exposure_period (?P<exposure_period>.+?) s\r\n)?'
    b'(.*^# Threshold_setting: (?P<threshold_energy>[^ ]+ eV))?'
    b'(.*^# Gain_setting: (?P<threshold_gain>[^\r\n]+))?'
    b'(.*^# Image_path: (?P<image_path>[^\r\n]+))?'
    b'(.*^# Wavelength (?P<wavelength>.*?) A)?'
    b'(.*^# Detector_distance (?P<detector_distance>.*?) m)?'
    b'(.*^# Beam_xy \((?P<beam_center_x>\d+\.\d+), (?P<beam_center_y>\d+\.\d+)\) pixels)?'
    b'(.*^# Flux (?P<photon_flux>[^\r\n]+))?'
    b'(.*^# Filter_transmission (?P<beam_attenuation>[^\r\n]+))?'
    b'(.*^# Start_angle (?P<start_angle>.*?) deg.)?'
    b'(.*^# Angle_increment (?P<angle_increment>.*?) deg.)?'
    b'(.*^# Phi (?P<phi>.*?) deg.)?'
    b'(.*^# Phi_increment (?P<phi_increment>.*?) deg.)?'
    b'(.*^# Chi (?P<chi>.*?) deg.)?'
    b'(.*^# Chi_increment (?P<chi_increment>.*?) deg.)?'
    b'(.*^# Oscillation_axis (?P<oscillation_axis>[^\r\n]+))?'
    b'(.*conversions="(?P<conversions>[^"]+)")?'
    b'(.*X-Binary-Size: (?P<binary_size>[^\r\n]+))?'
    b'(.*X-Binary-ID: (?P<binary_id>[^\r\n]+))?'
    b'(.*X-Binary-Element-Type: "(?P<binary_element_type>[^"]+)")?'
    b'(.*X-Binary-Element-Byte-Order: (?P<binary_element_byte_order>[^\r\n]+))?'
    b'(.*Content-MD5:\s*(?P<content_md5>[^\r\n]+))?'
    b'(.*X-Binary-Number-of-Elements: (?P<number_of_elements>[^\r\n]+))?'
    b'(.*X-Binary-Size-Fastest-Dimension: (?P<pixels_in_x>[^\r\n]+))?'
    b'(.*X-Binary-Size-Second-Dimension: (?P<pixels_in_y>[^\r\n]+))?'
    b'(.*X-Binary-Size-Padding: (?P<binary_padding>[^\r\n]+))?',
    flags=re.MULTILINE | re.DOTALL)

header_base = '''_array_data.data\r
;\r
--CIF-BINARY-FORMAT-SECTION--\r
Content-Type: application/octet-stream;\r
     conversions="{compression_algorithm}"\r
Content-Transfer-Encoding: BINARY\r
X-Binary-Size: {binary_size:d}\r
X-Binary-ID: 1\r
X-Binary-Element-Type: "{element_type}"\r
X-Binary-Element-Byte-Order: LITTLE_ENDIAN\r
Content-MD5: {md5_hash}\r
X-Binary-Number-of-Elements: {number_of_elements:d}\r
X-Binary-Size-Fastest-Dimension: {size_fastest_dimension:d}\r
X-Binary-Size-Second-Dimension: {size_second_dimension:d}\r
X-Binary-Size-Padding: {size_padding:d}\r
\r\n'''

header_end_mark = b'\x0C\x1A\x04\xD5'

end_binary_section = "\r\n--CIF-BINARY-FORMAT-SECTION----\r\n;\r\n"


def write(filename, data, header=None, size_padding=0):
    """
    Write CBF file
    :param filename: Filename of cbf file to write
    :param data: Data to write to cbf file (numpy array)
    :param header: Custom header to write to file
    :param size_padding: Number of bytes to pad at the end of the binary section
    :return: Compressed size
    """

    # Check input data
    if data.itemsize == 4:
        element_type = 'signed 32-bit integer'
    # elif data.itemsize == 2:
    #     element_type = 'signed 16-bit integer'
    else:
        raise TypeError(str(data.dtype))

    compression_algorithm = 'x-CBF_BYTE_OFFSET'

    # Compress data
    try:
        output_buffer = compress(data)
        output_buffer_size = output_buffer.size
    except:
        # The cbf compression was not able to compress the data
        compression_algorithm = 'x-CBF_NONE'
        output_buffer = data.tobytes()
        output_buffer_size = data.nbytes

    md5_hash = base64.b64encode(hashlib.md5(output_buffer).digest()).decode()

    # Write file
    file_handle = open(filename, 'wb')
    # file_handle.write(header['version'])
    # file_handle.write(header['convention'])
    # file_handle.write(header['contents'])
    file_handle.write(header_base.format(compression_algorithm=compression_algorithm,
                                         binary_size=output_buffer_size,
                                         number_of_elements=data.size,
                                         size_fastest_dimension=data.shape[1],
                                         size_second_dimension=data.shape[0],
                                         md5_hash=md5_hash, element_type=element_type,
                                         size_padding=size_padding).encode())
    file_handle.write(header_end_mark)
    file_handle.write(output_buffer)

    if size_padding:
        padding_bytes = b'\x00'*size_padding
        file_handle.write(padding_bytes)
    file_handle.write(end_binary_section.encode())

    file_handle.close()


def read(filename, metadata=True, parse_miniheader=False):
    """
    Read CBF files
    :param filename: Name of the file to read
    :param metadata: Return metadata alongside with the data
    :param parse_miniheader: Parse mini header as well
    :return: Data (namedtuple('data', 'metadata', 'miniheader')), None for both metadata/miniheader if False in params.
    """

    file_descriptor = open(filename, 'rb')
    file_content = file_descriptor.read()
    file_descriptor.close()

    # Find text/binary delimiter
    header_end_index = file_content.find(header_end_mark)

    # Read header
    file_header = file_content[:header_end_index]
    pattern = re.compile(r'X-Binary-([\w-]*)([\s:]*)(.*)')
    pattern_md5 = re.compile(r'Content-MD5:\s*(.*)')
    pattern_compression = re.compile(r'\s*conversions="(.*)"')
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
        else:
            m = pattern_md5.search(line)
            if m:
                header['md5'] = m.group(1).strip()
            else:
                m = pattern_compression.search(line)
                if m:
                    header['compression'] = m.group(1).strip()

    # print(header)

    # parse miniheader
    miniheader = dict()
    if parse_miniheader:
        try:
            m = miniheader_re.match(file_header)
            miniheader = m.groupdict()
        except:
            pass

        for k, v in miniheader.items():
            if not v:
                continue
            try:
                miniheader[k] = int(v)
            except (ValueError, TypeError) as e:
                try:
                    miniheader[k] = float(v)
                except (ValueError, TypeError) as e:
                    miniheader[k] = v.decode('utf-8')
                except:
                    pass

    # Read binary data
    input_buffer = file_content[header_end_index + len(header_end_mark):][:header['size']]
    # print(base64.b64encode(hashlib.md5(input_buffer).digest()))

    # Uncompress data
    if header['element_type'] == u'"signed 32-bit integer"': # DECTRIS PILATUS format
        data_type = numpy.int32
    elif '32' in header['element_type']:
        data_type = numpy.uint32
    # elif '16' in header['element_type']:
    #     data_type = numpy.uint16
    else:
        raise TypeError('Type not supported'+header['element_type'])

    if header['compression'] == "x-CBF_BYTE_OFFSET":
        data = uncompress(input_buffer, header['size_second_dimension'], header['size_fastest_dimension'], data_type)
    elif header['compression'] == "x-CBF_NONE":
        data = numpy.frombuffer(input_buffer, dtype=data_type)
        data = data.reshape((header['size_second_dimension'], header['size_fastest_dimension']))
    else:
        raise Exception('Compression type not supported')

    # Declaration data class / named tuple
    data_tuple = collections.namedtuple('Data', 'data metadata miniheader')

    return data_tuple(data, header, miniheader)


def compress(data):
    """
    Compress data
    :param data: Data to compress (numpy array)
    :return: Compressed data (numpy array - uint8-c-order)
    """
    output_buffer = numpy.ndarray(data.nbytes, dtype=numpy.uint8, order='C')
    compressed_size = cbf_c.compress(data, output_buffer)

    if compressed_size == 0:
        raise Exception("Unable to Compress")

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
