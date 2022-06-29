from queue import Queue


class Contact:
    def __init__(self, name, num, is_friend):
        self.contact_name = name
        self.contact_num = num
        self.friend = is_friend
        self.message_queue = Queue()