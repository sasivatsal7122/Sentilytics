import pymysql

# Connection parameters
conn_params = {
    "host": "127.0.0.0",
    "port": 3306,
    "user": "admin",
    "password": "admin",
    "db": "sentilytics",
}

# Connect to the database
conn = pymysql.connect(**conn_params)
cursor = conn.cursor()



# Add the foreign key constraint
alter_query = '''
    ALTER TABLE ScanInfo
    DROP COLUMN scan_id;
'''
cursor.execute(alter_query)


conn.commit()

# # Update the scan_id values in ScanInfo table
# update_query = '''
#     UPDATE ScanInfo s
#     JOIN Channels c ON s.scan_id = c.channel_id
#     SET s.scan_id = c.scan_id;
# '''
# cursor.execute(update_query)
# conn.commit()

# # Close the database connection
# cursor.close()
# conn.close()

print("Database update completed.")
