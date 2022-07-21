import unittest
import logging
import numpy
import cbf
import os

logging.basicConfig(level=logging.DEBUG)
base_dir_examples = "examples"


class TestGenerator(unittest.TestCase):
    def setUp(self):
        # Enable debug logging
        pass

    def test_write(self):
        for i in range(1000):
            logging.info("start")

            test_file = "test.cbf"

            # Ensure that file does not exist
            try:
                os.remove(test_file)
            except OSError:
                pass

            # 65536
            # 66600 cannot compress at all
            min_number = 0
            max_number = 66600
            max_number = 600
            max_number = 2147483647  # max value int32
            # max_number = 2147483648  # max value + 1int32 # will fail
            numpy_array = numpy.random.randint(min_number, max_number, (500, 400)).astype("int32")
            numpy_array[0][0] = max_number
            # numpy_array[0][0] = -1

            # numpy_array = numpy.empty((500, 400)).astype('int32')
            # numpy_array.fill(max_number)

            print(numpy_array[0][0])
            cbf.write(test_file, numpy_array)

            content = cbf.read(test_file)

            if not (numpy_array == content.data).all():
                print("NOT SAME")
                print((numpy_array == content.data).sum())

                print(content.data)
                print(content.metadata)
            print(content.metadata)
            print(i)
            self.assertTrue((numpy_array == content.data).all())

        # Remove test file
        os.remove(test_file)

    def test_read(self):
        logging.info("Checking reading example data")

        data = cbf.read(f"{base_dir_examples}/in16c_010001.cbf")

        # Random points of the image
        self.assertEqual(data.data[0][0], 1)
        self.assertEqual(data.data[0][-1], -2)  # Point with extreme value
        self.assertEqual(data.data[0][-2], 1)

        self.assertEqual(data.data[-1][0], -2)  # Point with extreme value
        self.assertEqual(data.data[-1][-1], -2)  # Point with extreme value
        self.assertEqual(data.data[-1][-2], 0)

        self.assertEqual(data.data[334][262], 1680)
        self.assertEqual(data.data[125][127], -2)  # Point with extreme value
        self.assertEqual(data.data[357][271], 214)

        data = cbf.read(f"{base_dir_examples}/run2_1_00148.cbf")
        # Random points of the image
        self.assertEqual(data.data[1169][1006], 20)
        self.assertEqual(data.data[1178][1030], 0)
        self.assertEqual(data.data[1223][1015], 2068)
        self.assertEqual(data.data[754][1859], 14)
        self.assertEqual(data.data[777][1707], 16)
        self.assertEqual(data.data[1302][1323], 98)


if __name__ == "__main__":
    unittest.main()
