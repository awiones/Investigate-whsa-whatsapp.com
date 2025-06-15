"""
MySQL Connection Script for adwhatm.com Investigation
Connects to MySQL database using credentials from .env file
"""

import pymysql
import argparse
import sys

def connect_to_mysql(host, port, username, password):
    """
    Attempt to connect to MySQL server with given credentials (no database selected)
    """
    try:
        print(f"Attempting to connect to MySQL server at {host}:{port}")
        print(f"Username: {username}")
        print(f"Password: {'*' * len(password)}")
        print("-" * 50)
        
        connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            ssl_ca=None,  # Accept self-signed SSL cert
            autocommit=True
        )
        
        print(f"✅ Successfully connected to MySQL Server (no database selected)")
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        print(f"✅ MySQL Server version: {version[0]}")
        
        # Try to show current database (should be None)
        cursor.execute("SELECT DATABASE();")
        database_name = cursor.fetchone()
        print(f"✅ Connected to database: {database_name[0]}")
        
        return connection, cursor
    except Exception as e:
        print(f"❌ Error while connecting to MySQL: {e}")
        return None, None

def main():
    parser = argparse.ArgumentParser(description='Connect to MySQL database')
    parser.add_argument('--host', default='38.85.201.87', help='MySQL host (default: 38.85.201.87)')
    parser.add_argument('--port', type=int, default=3306, help='MySQL port (default: 3306)')
    parser.add_argument('--database', help='Database name')
    parser.add_argument('--username', help='Username')
    parser.add_argument('--password', help='Password')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode after connection')
    
    args = parser.parse_args()
    
    # Default credentials from .env file
    credentials = [
        {
            'database': 'sql_kf_441jv_com',
            'username': 'sql_kf_441jv_com',
            'password': '52b5edce45e63'
        },
        {
            'database': '89qb5_com',
            'username': '89qb5_com',
            'password': 'hTbHNEPXdm4AiKp5'
        }
    ]
    
    # Use command line arguments if provided
    if args.database and args.username and args.password:
        credentials = [{
            'database': args.database,
            'username': args.username,
            'password': args.password
        }]
    
    connection = None
    cursor = None
    
    # Try each set of credentials
    for i, cred in enumerate(credentials, 1):
        print(f"\n🔄 Trying credential set {i}/{len(credentials)}")
        connection, cursor = connect_to_mysql(
            args.host, 
            args.port, 
            cred['username'], 
            cred['password']
        )
        
        if connection:
            break
        else:
            print(f"❌ Failed with credential set {i}")
    
    if not connection:
        print("\n❌ All connection attempts failed!")
        sys.exit(1)
    
    # Interactive mode
    if args.interactive:
        print("\n🔧 Entering interactive mode. Type 'quit' or 'exit' to leave.")
        print("You can execute SQL queries directly.")
        
        while True:
            try:
                query = input("\nSQL> ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                cursor.execute(query)
                
                if query.upper().startswith('SELECT') or query.upper().startswith('SHOW') or query.upper().startswith('DESCRIBE'):
                    results = cursor.fetchall()
                    if results:
                        for row in results:
                            print(row)
                    else:
                        print("No results returned")
                else:
                    print(f"Query executed successfully. Rows affected: {cursor.rowcount}")
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"❌ SQL Error: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Clean up
    if cursor:
        cursor.close()
    if connection:
        connection.close()
        print("\n✅ MySQL connection closed")

if __name__ == "__main__":
    main()