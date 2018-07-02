import mysql.connector
import bcrypt
from mysql.connector import errorcode

class DBConnectionManager():
    def __init__(self):
        config = {
            'user': 'websocket',
            'password': '|,LLG8kqt&^O:`CihKcwQR`21J&Iw^j\F$~4/G`*c0`m+DA|ln',
            'host': 'localhost',
            'database': 'TrailerScan',
            'raise_on_warnings': True,
        }
        
        try:
            self.__conn = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            
    def checkCredentials(self,authHash,password):
        passwordHash = password;
        result = {
                      'ID': ''
                    , 'name': ''
                    , 'successful': 'False'
                    , 'Error:':{
                          'message': 'Init error!'
                        , 'method': 'checkCredentials'
                    }
        }
        cursor = self.__conn.cursor()
        query = ("SELECT id, name, password FROM TrailerScan WHERE authHash = %s LIMIT 1")
        # Keep trailing ','! Elseway it isn't recognized as correct format 
        cursor.execute(query, (authHash,))
        for (id, name, password) in cursor:
            #Load hashed from the db and check the provided password
            if bcrypt.hashpw(passwordHash.encode(), password.encode()) == password:
                result = {
                      'ID': id
                    , 'name': name.encode()
                    , 'successful': 'True'
                }
            else:
                result = {
                      'ID': ''
                    , 'name': ''
                    , 'successful': 'False'
                    , 'Error:':{
                          'message': 'Password incorrect!'
                        , 'method': 'checkCredentials'
                    }
                }
        return result
            
    def insertGeolocation(self,id,data):
        try:
            result = {
                        'successful': 'False'
                        , 'Error:': {
                            'message':'Init Error!'
                        , 'method': 'insertGeolocation'
                        }
            }
            cursor = self.__conn.cursor()
            query_placeholders = ', '.join(['%s'] * (len(data)+1))
            query_columns = ', '.join(data)
            insert_query = ''' INSERT INTO geolocations (FK_TrailerScanID,%s) VALUES (%s) ''' %(query_columns,query_placeholders)
            print(insert_query)
            data = data.values()
            data.insert(0,id)
            print(data)
            cursor.execute(insert_query,tuple(data) )
            self.__conn.commit()
            result = {'successful': 'True'}
        except Exception as e:
            result = {'successful': 'False'
                    , 'Error':{
                        'message': str(e)
                        , 'method': 'insertGeolocation'
                    }
            }
            
        return result
        
if __name__ == "__main__":
    dbconn = DBConnectionManager()
    result = (dbconn.checkCredentials("$2y$10$PLLi9.bNwvaJpx2yAtkjluMlBDhgGvaI3Ol/lmOhqgywHoKC01jsm","$2y$10$VG4pN4bE2Ia6YFTARHvm0.gkaLBzGIzsVOVR0FW3ezw8ZjOCtnTpi"))
    