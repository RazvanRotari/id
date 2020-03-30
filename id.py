from datetime import datetime
import os
import threading

#Constants
INDEX_SIZE = 13
TIMESTAMP_SIZE = 41
NODE_SIZE = 10


TIMESTAMP_OFFSET = INDEX_SIZE + NODE_SIZE

INDEX_MASK = (1 << INDEX_SIZE) -1
TIMESTAMP_MASK = (1 << TIMESTAMP_SIZE) - 1
NODE_MASK = (1 << NODE_SIZE) - 1
START_TIME = 1585504547386

INCREMENT_VALUE = (1 << NODE_SIZE) 

#Mock implementation... almost
def node_id():
    return os.getenv("SHORELINE_NODE_ID", 42);

def timestamp():
    dt_obj = datetime.now()
    millisec = dt_obj.timestamp() * 1000
    return int(millisec)




"""


1. Please describe your solution to get_id and why it is correct i.e. guaranteed globally unique.  

Initial value:
	The id generator is in esence just a counter that is incremented with each call. The initial value is generate from the node_id and timestamp with this structure:

 [42 bits]  [13 bits]  [10 bits] 
 timestamp  index       node_id  

 - index will be initialized with 0
 - timestamp will be the number of milliseconds from "30.03.2020", the movement of the Unix epoch is to delay overflowing into the node_id part by a few tens years. 
 - node_id is unique for each node


Generation new ids:
	Increment atomically the counter and returning it.  
        Timestamp is not update, because if the number of request per milliseconds exceed 8192 we overflow into the timestamp part, if the number is small the timestamp part lags behind real time creating a sort of buffer . This delta is also useful for when the system crashes 


Why 2 nodes cannot generate the same id?
   Node_id is unique acros nodes, so 2 ids generate from 2 different nodes will have different prefixes.

Why one node cannot generate 2 identical ids in normal operation i.e. a single thead calling it?
	The counter is atomically incremented

Based on the information above uniqueness is guaranteed globally for normal operation. 

Note: This solution is similar to twitter snoflake and you have to believe me that most of the solution including custom epoch was develop before find about Snoflake. 

2.  Please explain how your solution achieves the desired performance i.e. 100,000 or more requests per second per node.  How did you verify this?

    The solution is as fast as a function call and an atomic increment, python has no native support for atomic variables so a mutex is used to be safe agains race conditions, causing a pretty huge bottleneck(the execution time dubles). 
    To verify there is a test that generates 100,000 ids multiple times and checks the duration 
 
### 3. Please enumerate possible failure cases and describe how your solution correctly handles each case.  How did you verify correctness?  Some example cases:  

    Problem: 
Race conditions, multiple threads try to generate an id, causing multple paralel read/write.
    Solution:
Avoided using a mutex, making the increment atomic

    Problem:
The system time is set to a time in the past.
    Solution:
Not handled, hard to provide a solution to this because we depend on the system time, high chances of generating a duplicate

    Problem:
The system time is set to a time in the future.
    Solution:
Not handled, hard to provide a solution to this because we depend on the system time, high chances of generating a duplicate in the future

    Problem:
The applition is restarted
    Solution:
When the process closes the timestamp part is saved to disk in a file wih the format "shoreline_${node_id}.state", after the restart if the value saved is equal or greater then the current time, the initial counter value will be the one saved + 1, if not the current timestamp is used. This protects agains scenarios when the load is hight and the index value overflowed in the timestamp part of the id. The file is delete while running to avoid using stale data. If for some reason the state is not save, check the following answer

    Problem:
The system crashes
    Solution:
There is no state save on disk so to initial counter value will use the current time, there is a risk of getting duplicated ids, but because the timestamp part lags behind the real time this is mitegated.

    Problem:
When sorting newer ids should be in the front of the list and older ones in the back
    Solution:
The timestamp part is the first one, followed by index, so the most significant bits are influence by time

    Problem:
The system is running for more then 69 years
    Solution:
Reclyle old ids



Cross language support:
    To be useful in a microservices enviorment a file base API is available, so that generating a new id is as simple as reading the value from a file in any file. Check id_fs.py for more information
Example:
```
# mkdir id_fs
# ./id_fs.py id_fs
# cat id_fs/id
687034620445738
```



"""


class IdGenerator:
    def __init__(self, node_id, timestamp):
        """
        sizeof(Id) = 64 bits

         [41 bits]  [13]           [10 bits] 
        timestamp  unique number   node_id   
        """
        self.index = ((timestamp & TIMESTAMP_MASK) << TIMESTAMP_OFFSET) | (node_id & NODE_MASK)
        self.lock = threading.Lock()

    def generate_id(self):
        with self.lock:
            self.index += INCREMENT_VALUE
            return self.index


#RAII impl
class PersistentIdGenerator(IdGenerator):
    def __init__(self, node_id, timestamp):
        self.filename  = "shoreline_{}.state".format(node_id)
        new_timestamp = 0
        if os.path.exists(self.filename):
            with open(self.filename, "r") as save_file:
                try:
                    new_timestamp = int(save_file.read())
                except Exception as e:
                    import sys
                    print("State file is illformed! Ignore it! ", file=sys.stderr)

        if new_timestamp >= timestamp:
            timestamp += new_timestamp + 1
        super().__init__(node_id, timestamp)
        # The open function will not be available when __del__ is called
        # also this clears the file. win win
        self.save_file = open(self.filename, "w")

    def __del__(self):
        self.save_file.write(str(self.index >> TIMESTAMP_OFFSET))

#Global state
generator = PersistentIdGenerator(node_id(), timestamp() - START_TIME)





"""
Generate an unique id
@Params: None
"""
def id():
    return generator.generate_id()

if __name__ == "__main__":
    print(id())
