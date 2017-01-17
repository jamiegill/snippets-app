import logging 
import argparse
import psycopg2

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")

def put(name, snippet):
    """
    Store a snippet with an associated name.DEBUG
    
    Returns the name and the snippet
    """
    logging.info("Storing snippet {!r}: {!r}".format(name,snippet))
    with connection, connection.cursor() as cursor:
        try:
            command = "insert into snippets values ({!r}, {!r})".format(name, snippet)
            cursor.execute(command)
        except psycopg2.IntegrityError:
            connection.rollback()
            command = "update snippets set message={!r} where keyword={!r}".format(snippet, name)
            cursor.execute(command)
    logging.debug("Snippet stored successfully.")
    return name, snippet
    
def get(name):
    """Retrieve the snippet with a given name.
    
    If there is no such snippet return '404: Snippet Not Found'
    
    Returns the snippet.
    """
    logging.info("Getting snippet information {!r}".format(name))
    
    
    with connection, connection.cursor() as cursor:
        cursor.execute("select keyword, message from snippets where keyword={!r}".format(name))
        snippet = cursor.fetchone()
    logging.debug("Snippet pulled successfully")
    if not snippet:
        # No snippet was found with that name.
        return "404: Snippet not Found"
    return snippet[1]
    
def search(name):
    """ Search for snippets using message content as the search string """
    logging.info("Searching for {!r}".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("select * from snippets where message like '%{}%'".format(name))
        name = cursor.fetchall()
        return name
    
def catalog():
    """ Display catalog of snippets if no argument is given """
    with connection, connection.cursor() as cursor:
        cursor.execute("select keyword from snippets order by keyword")
        rows = cursor.fetchall()
    logging.debug("Catalog pulled successfully")
    return rows
    
def main():
    """Main function"""
    logging.info("Construction parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
    
    # Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Get a snippet")
    get_parser.add_argument("name", help="Name of the snippet")
    
    # Subparser for the search command
    logging.debug("Constructing search subparser")
    search_parser = subparsers.add_parser("search", help="Search for message content")
    search_parser.add_argument("name", help="Use portion of snippet message to find snippet keyword and message")
    
    arguments = parser.parse_args()
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    
    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet,name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command == "search":
        names = search(**arguments)
        print("search results:")
        for name in names:
            print(name[0] + " " + name[1])
    else:
        snippets = catalog(**arguments)
        print ("current snippets keywords:")
        for snippet in snippets:
            print (snippet[0])
        
    
    
if __name__ == "__main__":
    main()
