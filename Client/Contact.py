from queue import Queue


class Contact:
    def __init__(self, name, num, is_friend):
        self.contact_name = name
        self.contact_num = num
        self.friend = is_friend
        self.message_queue = Queue() #{"用户": ,"内容": ,"类别": ,}
        self.image_list = []
