# Stands for any writer or reader
class Object:

    def __init__(self, id, type):
        # Thread id
        self.id = id
        # Thread type (False stands for reader and True for writer)
        self.type = type
        # The priority property is only usable for readers at the moment and does not mean anything to writers
        # if priority be True means it's the reader turn to be executed (prevent starvation problem) and if False
        # only if there were no writer in queue the reader can execute and other wise it has to wait
        self.priority = False


def read(id):
    # Id is identifier
    global shared_spaces
    global n_readers

    while True:
        # Calling get_access needs lock because at a moment only one reader or writer can attempt to get_access
        lock.acquire()
        # Type is False because of reader
        access = get_access(threading.current_thread().ident, False)
        lock.release()
        if access:
            n_readers += 1
            # Critical section
            # We need lock here to prevent massages that will be print on screen does not conflict
            lock.acquire()
            print("thread #"+str(id)+" read from shared space: ", shared_spaces)
            lock.release()
            n_readers -= 1
            break


def write(id):
    # Id is identifier
    global shared_spaces
    global n_writers

    while True:
        # Calling get_access needs lock because at a moment only one reader or writer can attempt to get_access
        lock.acquire()
        access = get_access(threading.current_thread().ident, True)
        lock.release()
        if access:
            # Only one writer can access to shared_space
            lock.acquire()
            n_writers += 1
            # Critical section
            # Writer action
            shared_spaces = threading.get_ident()
            print("thread #"+str(id)+" write to shared space: ", shared_spaces)
            n_writers -= 1
            lock.release()
            break


def get_access(id, type):
    # Here is my solution two second reader_writer problem that I mentioned as third solution before.
    # The algorithms allow writer to execute if there were no other writer or reader using shared_space
    # and a reader can access the shared_spaces if no writer be using it (another readers is ok) and no other
    # writer be in queue but there is special situation : If a reader ask for shared_spaces and there were writer(s)
    # in queue it has to wait but when one of that writers use shared_spaces it will be then reader turn to use
    # shared_space by this solution there will be no starvation for readers.
    # note: several readers can use shared_space simultaneously.

    global queue
    # Search for existing reader or writer in queue already
    existing_id = False
    existing_id_index = -1
    for j in range(queue.__len__()):
        if queue[j].id == id:
            existing_id_index = j
            existing_id = True
            break
    # Add not existing object(reader or writer) into queue
    if not existing_id:
        queue.append(Object(id, type))
        existing_id_index = queue.__len__() - 1

    # Check constraint for reader(type: False)
    if not queue[existing_id_index].type:
        if n_writers == 0:
            # Check if it has priority
            if queue[existing_id_index].priority:
                # Pop reader out from queue
                queue.pop(existing_id_index)
                return True
            else:
                # Check execution situation without priority
                temp=False
                for q in queue:
                    if q.type is True:
                        temp=True
                        break
                if not temp:
                    queue.pop(existing_id_index)
                    return True
        return False

    # Writer properties will be checks
    if queue[existing_id_index].type and n_writers == 0 and n_readers == 0:
        # Upcoming of existing_id_index give the existing readers Priority( because of the turn they had been wait!)
        for q in queue:
            if q.type is False:
                q.priority = True
        # pop out writer from queue
        queue.pop(existing_id_index)
        return True
    return False


import threading

n_readers = 0
n_writers = 0
shared_spaces = 0
lock = threading.Lock()
queue = []

for i in range(100):
    threading.Thread(target=read, args=(i,)).start()

for i in range(100, 200):
    threading.Thread(target=write, args=(i,)).start()



