import os
import sys
import inspect
import unittest
from utils.metadata_extractor import metadata_extractor
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.append(os.path.abspath(os.path.join('.', '')))


class MetadataExtractor(unittest.TestCase):
    def test_metadata_extractor(self):
        properties = metadata_extractor(fr"{parent_dir}/unit_tests/test_ge.py")
        self.assertIn("File Name", properties.keys())
        self.assertIn("Creation Date", properties.keys())
        self.assertIn("Last Edit Date", properties.keys())
        self.assertIn("File Size", properties.keys())
        self.assertIn("Hash Value", properties.keys())


if __name__ == "__main__":
    unittest.main()
