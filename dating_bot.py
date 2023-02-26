from vk_client import VK_Client
from vk_api.longpoll import VkLongPoll, VkEventType

from keyboard import hallo_keyboard, sql_keyboard, next_keyboard, more_keyboard
from sql_client import SQL_Client


class Messages:
    SUDJEST_MEETING = 'Я могу познакомить вас с кем-нибудь. Нажмите "Познакомиться", чтобы продолжить.'
    MEETING = 'познакомиться'
    HELL0 = 'Привет!'
    HELLO_VARIANTS = ['привет', 'привет!', 'hallo', 'hi', 'hi!', 'знакомства', 'dating']
    SEARCH_RESULT = "Я нашел для вас {} анкет c открытой страницей. Нажмите 'Дальше', чтобы посмотреть их."

    PHOTOS_NOT_AVAILABLE = 'Фотографии недоступны.'
    BEST_PHOTOS = 'Лучшие фотографии: '

    NEXT_PAIR = 'дальше'

    ERROR_SEARCH_PAIR = 'Ошибка при запросе поиска подходящих кандидатов'
    ERROR_SQL_REQUEST_PAIR = 'Ошибка при загрузке анкеты.'


class DatingBot:

    def __init__(self, access_token, community_token, db_config, dev_config):
        self.vk_client = VK_Client(access_token, community_token)
        self.session = self.vk_client.get_session()

        self.sql_client = SQL_Client(db_config)
        self.sql_client.connect()

        self.need_drop_table = dev_config.get('need_drop_table')
        self.need_print_msg = dev_config.get('need_print_msg')
        self.best_photos_count = dev_config.get('best_photos_count')
        self.search_pair_count = dev_config.get('search_pair_count')
        self.offset = dev_config.get('offset')

        self.total_pairs = 0

    def get_tuple_person(self, offset):
        # return self.sql_client.select_user(offset)
        return self.sql_client.select_user_by_id(offset=self.offset)

    def get_person_id(self, tuple_person):
        list_person = []
        for i in tuple_person:
            list_person.append(i)
        return str(list_person[2])

    def get_person_info(self, tuple_person):
        list_person = []
        for i in tuple_person:
            list_person.append(i)
        return f'{list_person[0]} {list_person[1]}, ссылка - {list_person[3]}'

    def if_need_drop_table(self):
        if self.need_drop_table:
            self.offset = 0
            self.total_pairs = 0
            self.sql_client.dropdb()

    def if_need_print_msg(self, message):
        if self.need_print_msg:
            print(message)

    def search_pair(self, user_id):
        open_count = 0

        search_params = self.vk_client.get_search_params(user_id=user_id, count=self.search_pair_count,
                                                         offset=self.offset)
        resp = self.vk_client.find_users(search_params)

        if resp:
            list_1 = resp['items']
            for person_dict in list_1:
                if person_dict.get('is_closed') == False:

                    first_name = person_dict.get('first_name')
                    last_name = person_dict.get('last_name')
                    vk_id = str(person_dict.get('id'))
                    vk_link = 'https://vk.com/id' + str(person_dict.get('id'))
                    print('index: {}, vk_id: {}'.format(open_count, vk_id))
                    open_count += 1
                    self.sql_client.insert_data_users(first_name, last_name, vk_id, vk_link)
                else:
                    continue

            self.total_pairs += open_count
            text = Messages.SEARCH_RESULT.format(open_count)
            self.vk_client.write_message_with_keyboard(user_id, text, next_keyboard)

        else:
            self.vk_client.write_message(user_id, Messages.ERROR_SEARCH_PAIR)

    def next_pair(self, user_id):
        print('offset {}:'.format(self.offset))
        tuple_person = self.get_tuple_person(self.offset)
        if tuple_person is None:
            if self.offset == self.total_pairs:
                # вывести сообщение что все пары закончились и предложить загрузить еще 
                text = 'Вы просмотрели всех кандидатов. Я могу найти новые знакомства. Нажмите "Загрузить еще" чтобы продолжить.'
                self.vk_client.write_message_with_keyboard(user_id,
                                                           text,
                                                           more_keyboard)
            else:
                print("[Error] person tuple is none type")
                print('offset: {}, total_pairs: {}'.format(self.offset, self.total_pairs))
                self.offset += 1
                self.next_pair(user_id)

                """self.vk_client.write_message_with_keyboard(user_id, 
                                                        Messages.ERROR_SQL_REQUEST_PAIR, 
                                                        next_keyboard)
                """
        else:
            person_info = self.get_person_info(tuple_person)
            person_id = self.get_person_id(tuple_person)

            print('person_ifo: {}'.format(person_info))
            print('person_id: {}'.format(person_id))

            self.vk_client.write_message(user_id, person_info)
            self.sql_client.insert_data_seen_users(person_id, self.offset)

            photos = self.vk_client.get_photos(person_id, self.best_photos_count)
            if not photos:
                text = Messages.PHOTOS_NOT_AVAILABLE
                self.vk_client.write_message_with_keyboard(user_id, text, next_keyboard)
            else:
                self.vk_client.send_photos(user_id, photos, Messages.BEST_PHOTOS, next_keyboard)

        self.offset += 1

    def listen(self):
        self.longpoll = VkLongPoll(self.session)

        for event in VkLongPoll(self.session).listen():

            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                user_id = event.user_id
                message = event.text.lower()

                self.if_need_print_msg(message)

                if message in Messages.HELLO_VARIANTS:
                    self.if_need_drop_table()
                    self.vk_client.write_message_with_keyboard(user_id, Messages.SUDJEST_MEETING, sql_keyboard)

                elif message == Messages.MEETING:
                    print('creating db...')
                    self.sql_client.createdb()
                    self.search_pair(user_id)

                elif message == Messages.NEXT_PAIR:
                    self.next_pair(user_id)

                elif message == 'загрузить еще':
                    # text = 'следующий шаг'
                    # self.vk_client.write_message(user_id, text)
                    self.search_pair(user_id)

                else:
                    self.vk_client.write_message_with_keyboard(user_id, Messages.HELL0, hallo_keyboard)
