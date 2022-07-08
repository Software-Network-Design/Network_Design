from queue import Queue


class Contact:
    def __init__(self, name, num, is_friend):
        self.contact_name = name    #接收者昵称（str）
        self.contact_num = num      #接收者用户ID（str） （群聊ID记为’000000‘）
        self.friend = is_friend     #接收者与当前用户是否为好友（boolean）
        self.message_queue = Queue()    #接收者与当前用户聊天历史记录队列 
                                        #{"用户": ,"内容": ,"类别": ,}
        self.image_list = []        #接收者与当前用户聊天历史记录中图片信息
