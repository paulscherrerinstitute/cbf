import unittest
import logging
import numpy
import cbf
import os

logging.basicConfig(level=logging.DEBUG)


def pre():
    logging.info('pre')


def post():
    logging.info('post')


class TestGenerator(unittest.TestCase):
    def setUp(self):
        # Enable debug logging
        pass

    def test_write(self):
        for i in range(1000):
            logging.info('start')

            test_file = 'test.cbf'

            # Ensure that file does not exist
            try:
                os.remove(test_file)
            except OSError:
                pass

            # 65536
            # 66600 cannot compress at all
            max_number = 66600
            numpy_array = numpy.random.randint(0, max_number, (500, 400)).astype('int32')
            numpy_array[0][0] = max_number

            # numpy_array = numpy.empty((500, 400)).astype('int32')
            # numpy_array.fill(max_number)


            print(numpy_array[0][0])
            cbf.write(test_file, numpy_array)

            content = cbf.read(test_file)

            if not (numpy_array == content.data).all():
                print('SAME')
                print((numpy_array == content.data).sum())

                print(content.data)
                print(content.metadata)
            print(content.metadata)
            print(i)
            self.assertTrue((numpy_array == content.data).all())

            # Remove test file
            # os.remove(test_file)


if __name__ == '__main__':
    unittest.main()
