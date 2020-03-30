#!/usr/bin/python3

import id
from datetime import datetime
import unittest
import threading

print("Will run for a few minutes")

def timestamp(date):
    dt_obj = datetime.strptime(date, '%d%b%Y')
    millisec = dt_obj.timestamp() * 1000
    return int(millisec)

class IdTest(unittest.TestCase):
    def test_simple_id(self):
        gen = id.IdGenerator(0, 0)
        self.assertEqual(gen.generate_id() , 1024)
        self.assertEqual(gen.generate_id() , 2048)
        self.assertEqual(gen.generate_id() , 3072)

    def test_with_valid_timestamp(self):
        gen = id.IdGenerator(0, timestamp('16Sep2012'))
        self.assertEqual(gen.generate_id() , 11305686034022401024)
        self.assertEqual(gen.generate_id() , 11305686034022402048)
        self.assertEqual(gen.generate_id() , 11305686034022403072)

    def test_with_valid_nodeId(self):
        gen = id.IdGenerator(42, 0)
        self.assertEqual(gen.generate_id() , 1066)
        self.assertEqual(gen.generate_id() , 2090)
        self.assertEqual(gen.generate_id() , 3114)

    def test_1_milion_ids(self):
        gen = id.IdGenerator(42, id.timestamp())
        ids = [ gen.generate_id() for _ in range(0, 1000000)]
        self.assertEqual(len(set(ids)) , len(ids))


class SpeedTest(unittest.TestCase):
    def test_speed_requirments_for_100k(self):
        import timeit
        time = timeit.timeit("[ gen.generate_id() for _ in range(0, 1000000)] ", setup="""
import id
gen = id.IdGenerator(42, id.timestamp())
""",number = 10)
        print('Generate 100k ids in {}s'.format(time/ 10))
        self.assertLess((time / 10 ) , 1)

    def test_speed_requirments_for_1(self):
        import timeit
        time = timeit.timeit("gen.generate_id()  ", setup="""
import id
gen = id.IdGenerator(42, id.timestamp())
""", number = 1000000)
        print('Generate 1 ids in {}s'.format(time/ 1000000))


class IdMultiThreadingTest(unittest.TestCase):
    class IdGenThread(threading.Thread):
        def __init__(self, gen, cond):
            super().__init__()
            self.gen = gen
            self.cond = cond

        def run(self):
            self.cond.wait()
            self.data = [self.gen.generate_id() for _ in range(0,100000)]


    def test_race_condition(self):
       gen = id.IdGenerator(42, id.timestamp())
       cond = threading.Event()
       def create_and_run(gen, conds):
           thread = IdMultiThreadingTest.IdGenThread(gen, cond)
           thread.start()
           return thread

       threads = [create_and_run(gen,cond) for _ in range(100)]
       cond.set() # Start all threads at once
       ids = []
       for thread in threads:
            thread.join()
            ids.extend(thread.data)
       self.assertEqual(len(set(ids)) , len(ids))


if __name__ == '__main__':
    unittest.main()
