import machine
try:
    import utime as time
except:
    import time
try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct
try:
    import uerrno as errno
except:
    import errno
    
    
class TZONE(object):
    
    def __init__(self, zone=0):
        self.zone = zone
        # time zones is supported
        self.TIME_ZONE = {-11: -11, -10: -10, -9: -9, -8: -8, -7: -7, -6: -6, -5: -5, \
        -4: -4, -3: -3, -2: -2, -1: -1, 0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, \
        7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14}
        # months of summer and winter time
        self.MONTH = {'sum': 3, 'win': 10} # 3 - march, 10 - october
        
        # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        self.NTP_DELTA = 3155673600
        # NTP server
        self.host = "pool.ntp.org"
    
    
    #Обновление времени по NTP    
    def getntp(self):
        print('Get UTC time from NTP server...')
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1b
       # Handling an unavailable NTP server error
        try:
            addr = socket.getaddrinfo(self.host, 123)[0][-1]
        except OSError: # as exc:
            #if exc.args[0] == -2:
                print('Connect NTP Server: Error resolving pool NTP')
                return 0
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
       # Handling NTP server long response error
        try:
            msg = s.recv(48)
        except OSError as exc:
            if exc.args[0] == errno.ETIMEDOUT:
                print('Connect NTP Server: Request Timeout')
                s.close()
                return 0
        s.close()
        val = struct.unpack("!I", msg[40:44])[0]
        return val - self.NTP_DELTA

    #Calculate the last Sunday of the month
    #https://ru.wikibooks.org/wiki/Реализации_алгоритмов/Вечный_календарь
    def sunday(self, year, month):
        for d in range(1,32):
            a = (14 - month) // 12
            y = year - a
            m = month + 12 * a -2
            if (((d + y + y // 4 - y // 100 + y // 400 + (31 * m) // 12)) % 7) == 0: # 0 - Sunday
                if d + 7 > 31: 
                    return d # Возращает число - последнее воскресенье месяца
    
    
    # We calculate summer or winter time now
    # В качестве параметра utc необходимо передать кортедж вида: (2018, 10, 22, 13, 31, 25, 0, 295)
    def adj_tzone(self, utc):
        # Если текущий месяц больше 3(март) 
        if utc[1] > self.MONTH['sum']:
            # Проверяем равен ли месяц 10(октябрь) или меньше 10 и меньше ли дата последнего воскресенья месяца
            if utc[1] <= self.MONTH['win'] and utc[2] < self.sunday(utc[0], self.MONTH['win']):
                print('TIME ZONE Summer:', self.TIME_ZONE[self.zone])
                return self.TIME_ZONE[self.zone] # Возращаем летнее время
        # Если месяц равен 3(март) проверяем больше ли дата последнего воскресенья месяца
        if utc[1] == self.MONTH['sum'] and utc[2] >= self.sunday(utc[0], self.MONTH['sum']):
            print('TIME ZONE Summer:', self.TIME_ZONE[self.zone])
            return self.TIME_ZONE[self.zone] # Возращаем летнее время
        else:
            print('TIME ZONE Winter:', self.TIME_ZONE[self.zone] - 1)
            return self.TIME_ZONE[self.zone] - 1 # Во всех остальных случаях возращаем зимнее время
