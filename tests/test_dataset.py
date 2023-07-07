import unittest
from corankco.ranking import Ranking
from corankco.dataset import Dataset
from corankco.element import Element

class TestDataset(unittest.TestCase):

    def setUp(self):
        # This method will be called before each test, it sets up the objects we'll use
        self.dataset_1 = Dataset([Ranking.from_list([{1}, {2, 3}, {4}]), Ranking.from_list([{1, 2}, {3}, {4}])])
        self.dataset_2 = Dataset([Ranking.from_list([{1, 2}, {3, 4}]), Ranking.from_list([{1}, {2}, {3}, {4}])])

    def test_init(self):
        # Test __init__ method
        self.assertEqual(len(self.dataset_1.rankings), 2)
        self.assertEqual(self.dataset_1.name, "")
        self.assertEqual(self.dataset_2.nb_elements, 4)

    def test_from_file(self):
        # Test from_file method with a test file
        dataset = Dataset.from_file("dataset_example")
        self.assertEqual(len(dataset.rankings), 2)
        # Add other assertions based on the expected content of the file

    def test_from_raw_list(self):
        # Test from_raw_list method
        dataset = Dataset.from_raw_list([[{1}, {2, 3}, {4}], [{1, 2}, {3}, {4}]])
        self.assertEqual(len(dataset.rankings), 2)
        self.assertEqual(dataset.nb_elements, 4)

    def test_remove_elements_rate_presence_lower_than(self):
        # Test remove_elements_rate_presence_lower_than method
        dataset = Dataset.from_raw_list([[{1, 2}, {3}, {4}], [{3}, {1}], [{3}, {1}], [{3}, {1}], [{2}]])
        # Test the elements count is as expected after removing elements with rate presence lower than 0.5
        self.assertEqual(dataset.nb_elements, 4)
        self.assertEqual(dataset.nb_rankings, 5)
        dataset.remove_elements_rate_presence_lower_than(0.5)
        self.assertEqual(dataset.nb_elements, 2)
        self.assertEqual(dataset.nb_rankings, 4)
    # Add more methods to test the other methods in your Dataset class

    def test_remove_empty_rankings(self):
        dataset = Dataset([Ranking.from_list([{1}, {2, 3}, {4}]), Ranking.from_list([{1, 2}, {3}, {4}])])
        self.assertEqual(dataset.nb_elements, 4)
        self.assertEqual(dataset.nb_rankings, 2)
        self.assertTrue(dataset.is_complete)
        self.assertFalse(dataset.without_ties)
        dataset.remove_empty_rankings()
        self.assertEqual(dataset.nb_elements, 4)
        self.assertEqual(dataset.nb_rankings, 2)
        self.assertTrue(dataset.is_complete)
        self.assertFalse(dataset.without_ties)

        dataset = Dataset.from_raw_list([[{1}, {2, 3}, {4}], [{1, 2}, {3}, {4}], []])
        self.assertEqual(dataset.nb_elements, 4)
        self.assertEqual(dataset.nb_rankings, 3)
        self.assertFalse(dataset.is_complete)
        self.assertFalse(dataset.without_ties)
        dataset.remove_empty_rankings()
        self.assertEqual(dataset.nb_elements, 4)
        self.assertEqual(dataset.nb_rankings, 2)
        self.assertTrue(dataset.is_complete)
        self.assertFalse(dataset.without_ties)

        for ranking in dataset.rankings:
            self.assertNotEqual(len(ranking), 0, "Empty ranking found in dataset.")

    def test_dataset_getitem(self):
        ranking1 = Ranking.from_list([{1, 2, 3}])
        ranking2 = Ranking.from_list([{4, 5, 6}])
        ranking3 = Ranking.from_list([{7, 8, 9}])
        dataset = Dataset([ranking1, ranking2, ranking3])
        self.assertEqual(dataset[0], ranking1)
        self.assertEqual(dataset[1], ranking2)
        self.assertEqual(dataset[2], ranking3)

    def test_dataset_contains(self):
        ranking1 = Ranking.from_list([{1, 2, 3}, {4, 5}])
        ranking2 = Ranking.from_list([{9, 5, 6}])
        ranking3 = Ranking.from_list([{7, 8, 9}])
        dataset = Dataset([ranking1, ranking2, ranking3])
        self.assertTrue(dataset.contains_element(1))
        self.assertTrue(dataset.contains_element(5))
        self.assertTrue(dataset.contains_element(9))
        self.assertTrue(dataset.contains_element(6))
        self.assertFalse(dataset.contains_element(10))
        self.assertFalse(dataset.contains_element(0))
        self.assertFalse(dataset.contains_element(45))

    def test_dataset_projection(self):
        ranking1 = Ranking.from_list([{1, 2, 3, 9}, {4, 5}])
        ranking2 = Ranking.from_list([{9, 5, 6}, {2}, {1}])
        ranking3 = Ranking.from_list([{7, 8, 9}])
        dataset = Dataset([ranking1, ranking2, ranking3])
        dataset2 = dataset.sub_problem_from_elements({Element(1), Element(2)})
        dataset3 = Dataset([Ranking.from_list([{1, 2}]), Ranking.from_list([{2}, {1}])])
        self.assertEqual(dataset2, dataset3)


if __name__ == "__main__":
    unittest.main()
