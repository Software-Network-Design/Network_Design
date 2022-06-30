from pathlib import Path
from queue import Queue

#
# path = Path('../file_received')
#
# path = path / "a.txt"
#
# with open(path, 'w') as file:
#     print("success")

temp_queue = Queue()
for i in range(5):
    temp_queue.put(i)

temp_queue2 = Queue()

while not temp_queue.empty():
    item = temp_queue.get()
    temp_queue2.put(item)
temp_queue = temp_queue2

print(temp_queue.empty())