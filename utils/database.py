import os
import sys
import sqlite3
import uuid
import inspect
from utils.Logs import get_logger

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
print(parent_dir)
logger = get_logger("utils.database")


# The Database class is defined to maintain the db functionalities like create_table, insert_table
class Database:

    def __init__(self, db_path="firmwaredatabase.db"):
        # The initialization function is available for all the methods with the db class
        self.dbname = fr"{parent_dir}/utils/{db_path}"
        self.dbdict = {
            'Fwfileid': '',
            'Fwfilename': '',
            'Manufacturer': '',
            'Modelname': '',
            'Version': '',
            'Type': '',
            'Releasedate': '',
            'Filesize': '',
            'Lasteditdate': '',
            'Checksum': '',
            'Embatested': '',
            'Embalinktoreport': '',
            'Embarklinktoreport': '',
            'Fwdownlink': '',
            'Fwfilelinktolocal': '',
            'Fwadddata': '',
            'Uploadedonembark': '',
            'Embarkfileid': '',
            'Startedanalysisonembark': ''
        }

    def create_table(self):
        """ The create_table functions connects to the db: firmwaredatabase if db is not available in the repo
        and if db is available it will carry the tasks like insert.
        A new functionality check need to be configured inorder to avoid multiple datasets for same data.
        The execute command in create_table fn will be used if table FWDB is not present in the file"""
        conn = sqlite3.connect(self.dbname)
        curs = conn.cursor()
        logger.info('As there is no db local file, a new %s will be created in the file directory.', self.dbname)
        create_command = """CREATE TABLE IF NOT EXISTS FWDB(
                            Fwfileid VARCHAR PRIMARY KEY,
                            Fwfilename VARCHAR NOT NULL,
                            Manufacturer TEXT NOT NULL,
                            Modelname VARCHAR NOT NULL,
                            Version TEXT NOT NULL,
                            Type TEXT NOT NULL,
                            Releasedate TEXT,
                            Filesize TEXT,
                            Lasteditdate TEXT,
                            Checksum TEXT,
                            Embatested TEXT NOT NULL,
                            Embalinktoreport TEXT,
                            Embarklinktoreport TEXT,
                            Fwdownlink TEXT NOT NULL,
                            Fwfilelinktolocal TEXT NOT NULL,
                            Fwadddata TEXT,
                            Uploadedonembark BOOLEAN DEFAULT false,
                            Embarkfileid VARCHAR DEFAULT NULL,
                            Startedanalysisonembark BOOLEAN DEFAULT false)"""
        curs.execute(create_command)
        logger.info('The database is created successfully in the code repository with the command: %s.', create_command)
        conn.commit()
        # curs.close()

    def db_check(self):
        # The function checks the db file, if not present it will create a db in the repo where database is used
        if self.dbname not in os.listdir('.'):
            logger.info('the db is not found so a new %s will be created', self.dbname)
            self.create_table()

    def insert_data(self, dbdictcarrier):
        self.db_check()
        # The insert_data function is used to update the new data in the db with dbdictcarrier as a dictionary input
        try:
            logger.info('As the %s is found, a new connection will be established.', self.dbname)
            conn = sqlite3.connect(self.dbname)
            logger.info('Connection details: %s.', conn)
            curs = conn.cursor()
            logger.info('A cursor is established on %s, with the details: %s.', self.dbname, curs)
            dbdict = self.dbdict
            for key in dbdict:
                dbdict[key] = dbdictcarrier[key]
                logger.info('The %s is updated with the Key: %s and Value: %s.', self.dbname, key, dbdict[key])

            if dbdict['Fwdownlink'] != '' and 'https://' in dbdict['Fwdownlink']:
                print(dbdict['Fwdownlink'])
                uuid_id = str(uuid.uuid5(uuid.NAMESPACE_URL, dbdict['Fwdownlink']))
                print(uuid_id)
            else:
                print(dbdict['Fwdownlink'])
                uuid_id = str(uuid.uuid1())
                print(uuid_id)

            if not os.path.isfile(fr'{parent_dir}/utils/database_txt_file/uuid_generated.txt'):
                print(os.path.exists('{parent_dir}/utils/database_txt_file'))
                os.mkdir(fr'{parent_dir}/utils/database_txt_file')
                with open(fr'{parent_dir}/utils/database_txt_file/uuid_generated.txt', 'w', encoding="utf-8") as uuid_file:
                    uuid_file.write('This file contains the UUID generated from download links & will be stored in DB.'
                                    + '\n')

            with open(fr'{parent_dir}/utils/database_txt_file/uuid_generated.txt', 'r', encoding="utf-8") as uuid_read:
                data = uuid_read.read()
            with open(fr'{parent_dir}/utils/database_txt_file/uuid_generated.txt', 'a', encoding="utf-8") as uuid_file:

                # print(data.split('\n'))
                if uuid_id not in data.split('\n'):
                    logger.info("The data is not present with respect to Fwfileid so, the data will be added into DB")
                    uuid_file.write(str(uuid_id + '\n'))
                    dbdict['Fwfileid'] = uuid_id
                    logger.info("The db is updated with the Fwfileid. as %s.", dbdict['Fwfileid'])
                    columns = "','".join(map(str, dbdict.keys()))
                    values = "','".join(map(str, dbdict.values()))
                    insert_command = f"INSERT INTO FWDB('{columns}') VALUES('{values}')"
                    curs.execute(insert_command)
                    logger.info('The db is inserted with the command %s.', insert_command)
                    conn.commit()
                    logger.info('The db commited is with data %s.', str(dbdict))

            # Prints the data in db
            curs.execute('SELECT * FROM FWDB')
            print(curs.fetchall())
            curs.close()

        except KeyError as error:
            logger.error("Error writing to db with data dict as: %s and with error as: %s", str(dbdictcarrier), error)
            print(error)
