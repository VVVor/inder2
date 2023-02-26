import psycopg2


class SQL_Client:
    def __init__(self, db_config) -> None:
        self.host = db_config.get('host')
        self.user = db_config.get('user')
        self.password = db_config.get('password')
        self.database = db_config.get('db_name')

    def connect(self):
        self.connection = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database)
        self.connection.autocommit = True

    def create_table_users(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS users(
                    id serial,
                    first_name varchar(50) NOT NULL,
                    last_name varchar(25) NOT NULL,
                    vk_id varchar(20) NOT NULL PRIMARY KEY,
                    vk_link varchar(50));"""
            )
        print("[INFO] Table USERS was created.")

    def create_table_seen_users(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS seen_users(
                id serial,
                vk_id varchar(50) PRIMARY KEY);"""
            )
        print("[INFO] Table SEEN_USERS was created.")

    def insert_data_users(self, first_name, last_name, vk_id, vk_link):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""INSERT INTO users (first_name, last_name, vk_id, vk_link) 
                VALUES ('{first_name}', '{last_name}', '{vk_id}', '{vk_link}')
                ON CONFLICT (vk_id) DO NOTHING;"""
            )

        print("[INFO] insert user with vk id:{} to table 'users'".format(vk_id))

    def insert_data_seen_users(self, vk_id, offset):
        print('insert_data_seen_users. vk_id:{}, offset:{}'.format(vk_id, offset))
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""INSERT INTO seen_users (vk_id) 
                VALUES ('{vk_id}')
                ON CONFLICT (vk_id) DO NOTHING;"""
            )
            '''
             cursor.execute(
                f"""INSERT INTO seen_users (vk_id) 
                VALUES ('{vk_id}')
                OFFSET '{offset}'
                ON CONFLICT (vk_id) DO NOTHING;"""
            )
            '''
        print("[INFO] insert user with vk id:{} to table 'seen_users'".format(vk_id))

    def select_user(self, offset):
        print('select_user offset:{}'.format(offset))
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""SELECT u.first_name,
                    u.last_name,
                    u.vk_id,
                    u.vk_link,
                    su.vk_id
                    FROM users AS u
                    LEFT JOIN seen_users AS su 
                    ON u.vk_id = su.vk_id
                    WHERE su.vk_id IS NULL
                    OFFSET '{offset}';"""
            )
            print(cursor.statusmessage)
            return cursor.fetchone()

    def select_user_by_id(self, offset):
        id = offset + 1
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""SELECT u.first_name,
                    u.last_name,
                    u.vk_id,
                    u.vk_link,
                    u.id,
                    su.vk_id
                    FROM users AS u
                    LEFT JOIN seen_users AS su 
                    ON u.vk_id = su.vk_id
                    WHERE su.vk_id IS NULL 
                    AND u.id = {id};"""
            )
            return cursor.fetchone()

    def drop_users(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """DROP TABLE IF EXISTS users CASCADE;"""
            )
        print('[INFO] Table USERS was deleted.')

    def drop_seen_users(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """DROP TABLE  IF EXISTS seen_users CASCADE;"""
            )
        print('[INFO] Table SEEN_USERS was deleted.')

    """ Getters """

    def is_table_exist(self, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name=%s", (table_name,)
            )
            exist = bool(cursor.rowcount)
            if exist:
                print("[INFO] table {} exist".format(table_name))
            else:
                print("[INFO] table {} not exist".format(table_name))
            return exist

    def is_users_table_exist(self):
        return self.is_table_exist('users')

    def is_seen_users_table_exist(self):
        return self.is_table_exist('seen_users')

    def createdb(self):
        if not self.is_users_table_exist():
            self.create_table_users()
            # в sql запросе о создании таблицы также есть условие IF NOT EXISTS, так что эта проверка не обязательна

        if not self.is_seen_users_table_exist():
            self.create_table_seen_users()

    def dropdb(self):
        self.drop_users()
        self.drop_seen_users()
