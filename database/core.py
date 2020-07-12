import sqlite3
from sqlite3 import Error as E
import datetime

# absolute database files
database = r'D:\Dev\yuanyu\yuanyuBS\database\sqlite.db'


# this should be the father class of all the Table
# each Table class includes properties:
# 1. table name
# each Table class contains the method to:
# 1. connect to the database
# 2. create this table
# 3. insert a single row to the table
# 4. insert all rows into the table
# 5. update table or get rid of the duplicance


class Table(object):
    '''Create table, store data and modify the tablexiaoji
    
    Each storage is a table in database. All methods are tools to modify this table.
    
    The class only contains table information and configuration, as sqlite has no configuration.
    
    Data stored in separate news table is in descent ordre, the newest news is in the last order
    '''
    def __init__(self, table_name=''):
        '''Each time a Table instance created, 
        there will be a table in database created or selected
        '''
        
        self.table_name = table_name
        self.create()
    
    def create(self):
        # table format is here with table name, not a safe method but unable to use other way
        sql_create_table = """CREATE TABLE IF NOT EXISTS {} (
            ariticle_id integer PRIMARY KEY, 
            title text NOT NULL, 
            link text NOT NULL, 
            img_link text, 
            source text, 
            genre text,
            added_date timestamp);""".format(self.table_name)
        
        # connect a database connection and curcor, could not be None
        conn = self.create_connection(database)
        if conn != None:
            self.conn = conn
            print('| Successfully set up connection |')
            cur = self.create_table(sql_create_table)
            if cur != None:
                self.cur = cur
                print("| Successfully get cursor |")
            else:
                return '| Error creating cursor |'
        else:
            return '| Error creating connection |'
        
    def create_connection(self, db_file):
        '''Create a database connection to a SQLlite database
        '''
        conn = None
        
        try:
            conn = sqlite3.connect(db_file)
            print(f'sqlite3 {sqlite3.version} database connected')
        except Error as e:
            print(e)
        finally:
            return conn
        
    def create_table(self, create_table_sql):
        '''Create a table with table name
        '''
        cur = None
        
        try:
            cur = self.conn.cursor()
            cur.execute(create_table_sql)
            print(f'Successfully create table: {self.table_name}')
            self.conn.commit()
        except E as e:
            print(e)
        finally:
            return cur
        
    def flow_insert(self, data): 
        '''Store a row at a time, used for flowing/iterated data
        
        Args:
            data: pure data in format: (xxx, xxx, ...)
        '''
        
        flow_insert_into_table = """
            INSERT INTO {} (title, link, img_link, source, added_date)
            VALUES (?, ?, ?, ?, ?)
        """.format(self.table_name)
        
        try:
            self.cur.execute(flow_insert_into_table, data)
            print(f'{self.table_name} adds flowing data: {data}')
            self.conn.commit()
        except E as e:
            print(e)
    
    def dump_insert(self, data):
        '''Stoer all data received, used for store
        '''
        
        dump_insert_into_table = """
            INSERT INTO {} (title, link, img_link, source, added_date)
            VALUES (?, ?, ?, ?, ?)
        """.format(self.table_name)
        
        try:
            self.cur.executemany(dump_insert_into_table, data)
            print(f'{self.table_name} adds dumping data: {data}')
            self.conn.commit()
        except E as e:
            print(e)
            
    def reserve(self):
        '''Reserve data after inserting
        '''
        self.remove_duplicate()
        
        # TODO: delete news three days ago
        # self.remove_overdated()
        
    def remove_duplicate(self):
        # this way to remove duplicate depends on rowid
        # must use group by to keep not-duplicated rows
        remove_sql_duplicate = """
        DELETE FROM {}
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM {}
            GROUP BY title
        )
        """.format(self.table_name, self.table_name)
        
        try:
            print('here')
            self.cur.execute(remove_sql_duplicate)
            print(f'Removed rows: {self.cur.rowcount}')
            self.conn.commit()
        except E as e:
            print(e)
    
    def remove_overdated(self):
        pass
    
    def merge_all_to_main_table(self, main_db_file=database):
        '''Merge all table contents (except id) into a main table
        
        This main table will be used in website development,
        machine learning and deep learning.
        
        Also, I think the frequency of certains news can be useful 
        for learning.
        
        So I won't remove duplicate news.
        '''
        
        selected_table_name = ''
        
        union_table_sql = '\tUNION\n'
        merge_all_table_sql = ''
        select_table_sql = 'SELECT title, link, img_link, source, added_date FROM {}\n'
        select_table_sqls = []
        
        # use table names to get sql union command
        tables = self.select_all_tables__(main_db_file)
        for table in tables:
            selected_table_name = ''.join(table)
            select_table_sqls.append(select_table_sql.format(selected_table_name))
        merge_all_table_sql = union_table_sql.join(select_table_sqls)
        
        # running sql union command to get data from all tables
        print(f'running sql command to merge table: {merge_all_table_sql}')
        
        try:
            self.cur.execute(merge_all_table_sql)
        except E as e:
            print(e)
            
        main_table_data = self.cur.fetchall()
        
        self.dump_insert(main_table_data)
        
    def select_all_tables__(self, db_file=database, close=False):
        table_names = ''
        
        try:
            self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'test';")
            table_names = self.cur.fetchall()
        except E as e:
            print(e)
        finally:
            if close:
                self.close_all()
            return table_names
        
    def empty_table(self):
        empty_table_sql = 'DELETE FROM {};'.format(self.table_name)
        
        # initiate_id_sql = '''
        # UPDATE sqlite_sequence SET seq = 0 WHERE name = "{}";
        # '''.format(self.table_name)
        
        print(f'Empty the tabel: {self.table_name}')
        
        try:
            print(f'1. Delete rows excuting sql command: {empty_table_sql}')
            self.cur.execute(empty_table_sql)
            # don't forget this one
            self.conn.commit()
            print('Successful!')
        except E as e:
            print(e)
            
        # try:
        #     print(f'2. initiate ip executing sql command: {initiate_id_sql}')
        #     self.cur.execute(initiate_id_sql)
        #     print('Successful')
        # except E as e:
        #     print(e)
        
    def select_columns(self, columns=''):
        '''Choose columns data
        
        The ? can only deliver values but not table name or columns
        I don't know if this way is safe enough
        
        Args:
            columns: str, contains coloumns separate by ,
            
        Returns:
            columns_data: data of the columns, tuple in tuple
        '''
        
        columns_data = None
                
        select_columns_sql = '''
            SELECT
                {}
            FROM 
                {};
        '''.format(columns, self.table_name)
                
        try:
            self.cur.execute(select_columns_sql)
            columns_data = self.cur.fetchall()
            if columns_data == None:
                print('Sorry, no data available in those columns\n')
        except E as e:
            print(e)
        
        return columns_data
            
    def close_all(self):
        self.cur.close()
        self.conn.close()
        print(f'{self.table_name} closed')
        
        
# class DB(object):
#     '''
#     Manipulate tables in database
    
#     Merge the data in all tables
#     '''

#     def __init__(self):
#         pass

#     def connect_database(self, db_file):
#         conn = None
    
#         try:
#             conn = sqlite3.connect(database)
#             print(f'sqlite3 {sqlite3.version} database connected')
#         except E as e:
#             print(e)
#         finally:
#             return conn
    
#     def create_connection(self, )