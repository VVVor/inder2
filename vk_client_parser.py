import datetime

class ParserException(Exception):
    pass

class VK_Client_Parser:

    AGE_LOW = 25
    AGE_HIGH = 45
    DEFAULT_CITY = 1 # Moscow

    def get_opposite_sex(self, resp):
        if not len(resp):
            raise ParserException({'message':'Response length is 0, but should be list with at least one element'})

        sex = resp[0].get('sex')
        if sex == 1:
            return 2
        else:
            return 1
        
    def get_current_age(self, resp):
        date = resp[0].get('bdate')
        date_list = date.split('.')
        if len(date_list) == 3:
            year = int(date_list[2])
            year_now = int(datetime.date.today().year)
            return year_now - year
        else:
            return False
        
    def get_age_low(self, resp):
        if not len(resp) or not resp[0] or not resp[0].get('bdate'):
            print ('[INFO] Use default age low integer for parser.get_age_low')
            return VK_Client_Parser.AGE_LOW
            #raise ParserException({'message':'Response length is 0, but should be list with at least one element'})

        return self.get_current_age(resp)

    def get_age_high(self, resp):
        if not len(resp) or not resp[0] or not resp[0].get('bdate'):
            print('[INFO] Use default age high integer for parser.get_age_high')
            return VK_Client_Parser.AGE_HIGH
            #raise ParserException({'message':'Response length is 0, but should be list with at least one element'})

        return self.get_current_age(resp)
    
    def get_city_id(self, resp):
        if not len(resp) or not resp[0] or not resp[0].get('city') or not resp[0].get('city').get('id'):
            print ('[INFO] Use default city index for parser.get_city_id')
            return VK_Client_Parser.DEFAULT_CITY
            #raise ParserException({'message':'Response length is 0, but should be list with at least one element'})
        
        city = resp[0].get('city')
        city_id = city.get('id')
        return city_id
        
