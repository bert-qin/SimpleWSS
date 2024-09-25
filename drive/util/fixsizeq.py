import queue


class FixSizeQ(queue.Queue):
    def __init__(self, size):
        super().__init__(maxsize=size)
        self.max_size = size

    def put(self, item, block=True, timeout=None):
        if self.qsize() >= self.max_size:
            self.get()
        super().put(item, block, timeout)

    def to_list(self):
        return list(self.queue)
    
    def clear(self):
        while not self.empty():
            self.get()


if __name__ == "__main__":
    max_size = 5
    q = FixSizeQ(max_size)

    for i in range(10):
        q.put(i)
        print(f"Enqueued: {i}, Current Queue: {list(q.queue)}")

    print("Dequeuing elements:")
    while not q.empty():
        print(f"Dequeued: {q.get()}, Current Queue: {list(q.queue)}")
