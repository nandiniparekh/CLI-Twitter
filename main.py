import sqlite3
import getpass
from datetime import date, datetime
import sys

connection = None
cursor = None

def connect(path):
    ## Instantiates global variables
    global connection, cursor

    # Connects to database and equips cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return


def define_tables():
    ## This function should only be called if a database is not provided
    global connection, cursor

    # Dropping tables if they exist
    all_tables = [
        "includes",
        "lists",
        "retweets",
        "mentions",
        "hashtags",
        "tweets",
        "follows",
        "users"
    ]
    for table in all_tables:
        drop_query = f"DROP TABLE IF EXISTS {table};"
        cursor.execute(drop_query)

    # Create tables
    users_query = '''
        CREATE TABLE users (
            usr         int,
            pwd	        text,
            name        text,
            email       text,
            city        text,
            timezone    float,
            primary key (usr)
        );
    '''

    follows_query = '''
        CREATE TABLE follows (
            flwer       int,
            flwee       int,
            start_date  date,
            primary key (flwer,flwee),
            foreign key (flwer) references users,
            foreign key (flwee) references users
        );
    '''

    tweets_query = '''
        CREATE TABLE tweets (
            tid	        int,
            writer      int,
            tdate       date,
            text        text,
            replyto     int,
            primary key (tid),
            foreign key (writer) references users,
            foreign key (replyto) references tweets
        );
    '''

    hashtags_query = '''
        CREATE TABLE hashtags (
            term        text,
            primary key (term)
        );
    '''

    mentions_query = '''
        CREATE TABLE mentions (
            tid         int,
            term        text,
            primary key (tid,term),
            foreign key (tid) references tweets,
            foreign key (term) references hashtags
        );
    '''

    retweets_query = '''
        CREATE TABLE retweets (
            usr         int,
            tid         int,
            rdate       date,
            primary key (usr,tid),
            foreign key (usr) references users,
            foreign key (tid) references tweets
        );
    '''

    lists_query = '''
        CREATE TABLE lists (
            lname        text,
            owner        int,
            primary key (lname),
            foreign key (owner) references users
        );
    '''

    includes_query = '''
        CREATE TABLE includes (
            lname       text,
            member      int,
            primary key (lname,member),
            foreign key (lname) references lists,
            foreign key (member) references users
        );
    '''


    # Create every table
    create_queries = [users_query, follows_query, tweets_query, hashtags_query, mentions_query, retweets_query, lists_query, includes_query]
    for query in create_queries:
        cursor.execute(query)

    connection.commit()
    return


def main_screen():
    ## Main screen for logging in, signing up, or exiting. First and last encountered
    print("\nWelcome to the Main Screen")
    print("Select an option from the choices below")
    print("[1] Log in")
    print("[2] Sign up")
    print("[3] Exit")

    # Validate choice
    try:
        choice = int(input("Please enter your choice: "))
    except ValueError:
        print("The choice must be an integer.\n")
        main_screen()   

    if choice == 1:
        # Log in
        user_id = get_and_check_entries("userid")
        password = get_and_check_entries("password")

        # Check if user_id and password are valid
        valid = login_check(user_id, password)

        if valid:
            print("Login successful.\n")
            user_dashboard(user_id)
        else:
            print("Login unsuccessful. Either the user name or the password are incorrect.\n")
            main_screen()
    
    elif choice == 2:
        # Sign up
        sign_up()

    elif choice == 3:
        # Exit
        exitSafely()

    else:
        print("Invalid choice. Please try again.\n")
        main_screen()


def get_and_check_entries(param):
    ## Examines all user fields for validity
    valid = True

    while valid:
        try:
            if (param == "userid"):
                parameter = int(input("Enter user id: "))
            elif (param == "password"):
                parameter = getpass.getpass("Enter password: ")
            elif (param == "timezone"):
                parameter = float(input("Enter timezone: "))
            else: 
                parameter = input(f"Enter {param}: ")
            if (parameter == ''):
                raise NameError("This field cannot be left blank. Please enter a value.\n")
            valid = False
        except NameError as e:
            print(e)
        except ValueError:
            print("This field only accepts numeric values. Please re-enter\n")
    return parameter


def login_check(user_id, password):
    ## Verifies user_id and password are valid
    global connection, cursor
    
    cursor.execute("""
            SELECT usr 
            FROM users 
            WHERE usr = :user_name AND pwd = :password
""", {'user_name': user_id, 'password': password})
    
    if (cursor.fetchall() == []):
        return False
    else:
        return True


def sign_up():
    ## Signs up non-registered users
    global connection, cursor
    print("\nSign Up\n")

    invalid = True

    # Verifies user name free
    while invalid:
        user_id = get_and_check_entries("userid")
        cursor.execute("""
                    SELECT * 
                    FROM users 
                    WHERE usr = :user_name""", 
                    {'user_name': user_id})
        if (cursor.fetchall() != []):
            print("This username is already taken. Please enter another name\n")
        else:
            invalid = False

    # Gets input for all user-related fields
    password = get_and_check_entries("password")
    
    name = get_and_check_entries("name")
    email = get_and_check_entries("email")
    city = get_and_check_entries("city")
    timezone = get_and_check_entries("timezone")

    new_user = {
        'user_name': user_id,
        'password': password,
        'name': name,
        'email': email,
        'city': city,
        'timezone': timezone
    }

    # Stores new user in database
    cursor.execute("""
            INSERT INTO users(usr, pwd, name, email, city, timezone) VALUES
                   (:user_name, :password,:name, :email, :city, :timezone)
    """, new_user)    
    connection.commit()

    print("Sign up successful\n")
    main_screen()
    return


def user_dashboard(user_id):
    ## Interemediary function to get all followed user tweets post-login
    global connection, cursor, u_tweets

    # Get user name
    cursor.execute("""
            SELECT name 
            FROM users
            WHERE usr = :user_id
""", {'user_id': user_id})
    
    user_name = cursor.fetchone()
    print(f"Welcome, {user_name[0]} \n")
    
    # Get all followed user tweets
    cursor.execute("""
            SELECT tweets.tid, tweets.text, tweets.tdate, 
                (SELECT COUNT(*) FROM retweets WHERE retweets.tid = tweets.tid) as retweet_count, 
                (SELECT COUNT(*) FROM tweets as t2 WHERE t2.replyto = tweets.tid) as reply_count 
                FROM tweets, follows
            WHERE flwer = :user_id AND writer = flwee
            ORDER BY tweets.tdate DESC
    """, {'user_id': user_id})
    
    u_tweets = cursor.fetchall()

    if (u_tweets == []):
        print("You are all caught up.\n")

    user_dashboard_options(user_id, u_tweets)        
    return
    

def user_dashboard_options(user_id, tweet_list = None):
    ## Displays any tweets to be viewed and lists primary functionality options
    print("**************************************************************************\n")
    print("Dashboard Options\n")
    remaining_tweets = []
    display_tweets = []
    if tweet_list:
        remaining_tweets, display_tweets = show_next_tweets(tweet_list)

    print("  Enter the associated number to perform the respective action")

    # User has not viewed all tweets
    while remaining_tweets:
        print(f"[1] See more tweets ({len(remaining_tweets)} remaining)")
        print("[2] Search for tweets")
        print("[3] Search for users")
        print("[4] Compose a tweet")
        print("[5] List followers")
        print("[6] Logout")
        
        dashboard_choice = input("Please enter your choice: ")

        if ((dashboard_choice in ['A', 'B', 'C', 'D', 'E', 'a', 'b', 'c', 'd', 'e'])):
            operate_on_tweet(user_id, dashboard_choice, display_tweets)
            user_dashboard_options(user_id, display_tweets + remaining_tweets)

        elif (dashboard_choice == '1'):
            user_dashboard_options(user_id, remaining_tweets)

        elif (dashboard_choice == '2'):
            result_tweets = search_tweets()
            user_dashboard_options(user_id, result_tweets)
        
        elif (dashboard_choice == '3'):
            search_users(user_id)
            user_dashboard_options(user_id, remaining_tweets)

        elif (dashboard_choice == '4'):
            compose_tweet(user_id)
            user_dashboard_options(user_id, remaining_tweets)

        elif (dashboard_choice == '5'):
            list_followers(user_id)
            user_dashboard_options(user_id, remaining_tweets)

        elif (dashboard_choice == '6'):
            print("Logged out successfully\n")
            main_screen()
        
        else:
            print("Incorrect choice. Please re-enter")
            user_dashboard_options(user_id, tweet_list)

    # No additional tweets to display        
    while True:
        print("[1] Search for tweets")
        print("[2] Search for users")
        print("[3] Compose a tweet")
        print("[4] List followers")
        print("[5] Logout")

        choice = input("Please enter your choice: ")

        if ((choice in ['A', 'B', 'C', 'D', 'E', 'a', 'b', 'c', 'd', 'e']) and display_tweets):
            # Go to the tweet
            operate_on_tweet(user_id, choice.upper(), display_tweets)

            # See if more tweet exploration is desired
            user_dashboard_options(user_id, display_tweets)

        if choice == '1':
            result_tweets = search_tweets()
            user_dashboard_options(user_id, result_tweets)
        elif choice == '2':
            search_users(user_id)
            user_dashboard_options(user_id)
        elif choice == '3':
            compose_tweet(user_id)
            user_dashboard_options(user_id)
        elif choice == '4':
            list_followers(user_id)
            user_dashboard_options(user_id)
        elif choice == '5':
            main_screen()
        else:
            print("Incorrect choice. Please re-enter")
            user_dashboard_options(user_id, display_tweets)


def show_next_tweets(tweet_list):
    ## Shows 5 tweets at a time, splitting by tweets displayed and conserved for viewing
    print("  Enter the associated letter to view more information about the tweet")

    # More than five so split
    if len(tweet_list) > 5:
        display_tweets = tweet_list[:5]
        remaining_tweets = tweet_list[5:]
        for i, tweet in enumerate(display_tweets, start=1):
            if i == 1:
                print(f"[A]: {tweet[1]}, {tweet[2]}")
            elif i == 2:
                print(f"[B]: {tweet[1]}, {tweet[2]}")
            elif i == 3:
                print(f"[C]: {tweet[1]}, {tweet[2]}")
            elif i == 4:
                print(f"[D]: {tweet[1]}, {tweet[2]}")
            else:
                print(f"[E]: {tweet[1]}, {tweet[2]}")

    # Maxiumum 5 so no tweets remaining after display
    else:
        for i, tweet in enumerate(tweet_list, start=1):
            if i == 1:
                print(f"[A]: {tweet[1]}, {tweet[2]}")
            elif i == 2:
                print(f"[B]: {tweet[1]}, {tweet[2]}")
            elif i == 3:
                print(f"[C]: {tweet[1]}, {tweet[2]}")
            elif i == 4:
                print(f"[D]: {tweet[1]}, {tweet[2]}")
            else:
                print(f"[E]: {tweet[1]}, {tweet[2]}")
        display_tweets = tweet_list
        remaining_tweets = []
    
    return remaining_tweets, display_tweets


def operate_on_tweet(user_id, choice, display_tweets):
    ## Displays selected tweet information and provides option to reply or retweet
    index = ord(choice.upper()) - 65  # Convert letter to index (A=0, B=1, etc.)
    selected_tweet = display_tweets[index]

    # Displays tweet stats
    print(f"\nSelected tweet: Tweet {choice} has {selected_tweet[3]} retweets and {selected_tweet[4]} replies")

    # Provide options to reply or retweet
    while True:
        print("[1] Compose a reply")
        print("[2] Retweet")
        print("[3] Exit")

        option = input("Please enter your choice: ")

        if option == '1':
            reply_text = input("\nEnter your reply: ")
            post_reply(user_id, selected_tweet[0], reply_text)
            user_dashboard_options(user_id)
        elif option == '2':
            tweet_content = selected_tweet[1]
            post_retweet(user_id, selected_tweet[0], tweet_content)
            user_dashboard_options(user_id)
        elif option == '3':
            return
        else:
            print("Invalid choice. Please try again.")

def search_tweets():
    ## Function to search for tweets
    print("Searching for tweets...")
    hashtag_results = []
    text_results = []

    # Get user input
    keywords = get_input_keywords()

    # Run separate queries for hashtags vs text
    for keyword in keywords:
        if keyword.startswith('#'):
            cursor.execute('''
                SELECT tweets.tid, tweets.text, tweets.tdate, 
                (SELECT COUNT(*) FROM retweets WHERE retweets.tid = tweets.tid) as retweet_count, 
                (SELECT COUNT(*) FROM tweets as t2 WHERE t2.replyto = tweets.tid) as reply_count 
                FROM tweets 
                JOIN mentions ON tweets.tid = mentions.tid 
                JOIN hashtags ON mentions.term = hashtags.term 
                WHERE lower(hashtags.term) = ? 
                ORDER BY tweets.tdate DESC
            ''', (keyword[1:].lower(),))
            hashtag_results.extend(cursor.fetchall())
        else:
            cursor.execute('''
                SELECT tweets.tid, tweets.text, tweets.tdate, 
                (SELECT COUNT(*) FROM retweets WHERE retweets.tid = tweets.tid) as retweet_count, 
                (SELECT COUNT(*) FROM tweets as t2 WHERE t2.replyto = tweets.tid) as reply_count 
                FROM tweets 
                WHERE tweets.text LIKE ? 
                ORDER BY tweets.tdate DESC
            ''', (f'%{keyword}%',))
            text_results.extend(cursor.fetchall())


    # Combine and remove duplicates, sorting thereafter
    combined_results = sorted(set(hashtag_results + text_results), key=lambda x: x[2], reverse=True)
    combined_results_list = list(combined_results)

    return combined_results_list
    

def get_input_keywords():
    ## Get desired search keywords from user
    keywords = []

    print("Keywords can be hashtags [#search] or text")
    while True:
        response = input("\nWould you like to enter a keyword? (yes/no): ")
        if response.lower() == 'no':
            break
        elif response.lower() == 'yes':
            keyword = input("\nEnter a keyword: ")
            keywords.append(keyword)
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
    return keywords
    

def compose_tweet(user_id):
    ## Function to compose a tweet
    print(f"\nComposing a tweet...")

    # Get input
    tweet_content = input("Enter your tweet: ")

    if tweet_content == "":
        print("User input required")
        compose_tweet(user_id)

    # Get hashtags
    hashtags = extract_hashtags(tweet_content)

    # Save the tweet and hashtags to the database
    #print(f"Posting {tweet_content}, with hashtags {hashtags}")
    post_tweet(user_id, tweet_content, hashtags)

    print("Tweet posted successfully.")


def extract_hashtags(tweet_content):
    ## Extract hashtags from tweet content
    words = tweet_content.split()

    hashtags= []
    for word in words:
        if word.startswith('#'):
            hashtags.append(word[1:].lower())

    return hashtags


def post_tweet(user_id, tweet_content, hashtags):
    ## Determine available tweet id and compile tweet information
    cursor.execute("SELECT COUNT(*) FROM tweets")
    tweet_count = cursor.fetchone()[0]
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Record in tweets
    cursor.execute("INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (?, ?, ?, ?, ?)",
                   (tweet_count + 1, user_id, current_date, tweet_content, None))
    tweet_id = cursor.lastrowid

    # Record in hashtags and mentions
    for hashtag in hashtags:
        hashtag_tuple = (hashtag,)
        cursor.execute("INSERT OR IGNORE INTO hashtags (term) VALUES (?);", hashtag_tuple)
        cursor.execute("SELECT term FROM hashtags WHERE term = ?;", hashtag_tuple)
        hashtag_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO mentions (tid, term) VALUES (?, ?);", (tweet_id, hashtag_id))

    connection.commit()


def post_retweet(user_id, tweet_id, tweet_content):
    ## Function to retweet a tweet
    # Check if the retweet already exists
    cursor.execute("SELECT * FROM retweets WHERE usr = ? AND tid = ?", (user_id, tweet_id))
    existing_retweet = cursor.fetchone()

    if existing_retweet:
        print("You have already retweeted this tweet.")
    else:
        # Record in tweets
        cursor.execute("SELECT COUNT(*) FROM tweets")
        tweet_count = cursor.fetchone()[0]
        current_date = datetime.now().strftime('%Y-%m-%d')

        cursor.execute("INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (?, ?, ?, ?, ?)",
                    (tweet_count + 1, user_id, current_date, tweet_content, None))
        
        new_tweet_id = cursor.lastrowid

        # Record in hashtags and mentions
        hashtags = extract_hashtags(tweet_content)
        for hashtag in hashtags:
            hashtag_tuple = (hashtag,)
            cursor.execute("INSERT OR IGNORE INTO hashtags (term) VALUES (?);", hashtag_tuple)
            cursor.execute("SELECT term FROM hashtags WHERE term = ?;", hashtag_tuple)
            hashtag_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO mentions (tid, term) VALUES (?, ?);", (new_tweet_id, hashtag_id))

        # Record in retweets
        cursor.execute("INSERT INTO retweets (usr, tid, rdate) VALUES (?, ?, datetime('now'));", (user_id, tweet_id))
        connection.commit()

        print(f"Tweet has been retweeted.")


# Function to reply to a tweet
def post_reply(user_id, tweet_id, reply_text):
    ## Record reply in tweets
    # Determine original tweet writer
    cursor.execute("SELECT writer FROM tweets WHERE tid = ?", (tweet_id,))
    replied_user_id = cursor.fetchone()
    if replied_user_id:
        replied_user_id =  replied_user_id[0]
    else:
        print("reply problem")

    # Determine available tweet id
    cursor.execute("SELECT COUNT(*) FROM tweets")
    tweet_count = cursor.fetchone()[0]
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Record reply in tweets
    cursor.execute("INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (?, ?, ?, ?, ?)",
                   (tweet_count + 1, user_id, current_date, reply_text, replied_user_id))
    
    new_tweet_id = cursor.lastrowid

    # Record in hashtags and mentions
    hashtags = extract_hashtags(reply_text)
    for hashtag in hashtags:
        hashtag_tuple = (hashtag,)
        cursor.execute("INSERT OR IGNORE INTO hashtags (term) VALUES (?);", hashtag_tuple)
        cursor.execute("SELECT term FROM hashtags WHERE term = ?;", hashtag_tuple)
        hashtag_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO mentions (tid, term) VALUES (?, ?);", (new_tweet_id, hashtag_id))
    
    connection.commit()
    print(f"Replied to tweet with ID {tweet_id}.")


def search_users(user_id):
    ## Search users by id, intermediary function
    while(True):
        search_keyword = input("Enter a keyword to search for a user or press 0 to exit: ")
        if (search_keyword == ''):
            print("Invalid input, please try again.")
            continue
        elif (search_keyword == '0'):
            break
        else:
            search_user_keyword(search_keyword, user_id)
            break

def search_user_keyword(keyword, user_id):
    ## Function to search users
    # Obtains user records where the name contains the keyword
    cursor.execute("""
        SELECT usr, name, city FROM users 
        WHERE LOWER(name) LIKE LOWER(?) 
        ORDER BY LENGTH(name), name ASC
        LIMIT 5;""", ('%' + keyword + '%',))
    
    users_by_name = cursor.fetchall()

    # If no users are found, the user is prompted to enter a new keyword or end the search
    if (len(users_by_name) == 0):
        new_keyword = input("No users found. Please try again or press 1 to end search.")
        if (new_keyword == '1'):
            return
        search_user_keyword(new_keyword, user_id)
    
    # Obtains user records where the city contains the keyword
    cursor.execute("""
        SELECT usr, name, city FROM users 
        WHERE LOWER(city) LIKE LOWER(?) AND LOWER(name) NOT LIKE LOWER(?) 
        ORDER BY LENGTH(city), city ASC
        LIMIT 5;""", ('%' + keyword + '%', '%' + keyword + '%'))
    
    users_by_city = cursor.fetchall()

    # Combining the list of users by name and users by city
    total_users = users_by_name + users_by_city
    users_list = [user[0] for user in total_users]
    
    index = 0

    # Printing the first 5 users
    while index < len(total_users):

        # Printing the user ID, name and city of each user
        for user in total_users[index:index+5]:
            print(user)  
        index += 5  

        # If there are more than 5 users, the user is prompted to see more results or exit
        if index < len(total_users):
            while(True):
                choice = input("\nPress 1 to see more results, 2 to see more information about a user or press 3 to exit: ")
                if (choice == '1'):
                    break
                elif (choice == '2'):
                    show_user_info(users_list, user_id)
                    break
                elif (choice == '3'):
                    break
                else:
                    print("Invalid input")
                    continue
        else:
            while(True):
                choice = input("\nPress 1 to see more information about a user or 2 to exit: ")
                if (choice == '1'):
                    show_user_info(users_list, user_id)
                    break
                elif (choice == '2'):
                    break
                else:
                    print("Invalid input")
                    continue


def show_user_info(user_list, user_id):
    ## Shows selected user info and allows further function selection
    while (True):
        usr = input("Enter the user ID of the user to see more information: ")

        # Input validation
        if (usr == ''):
            print("Invalid input, please try again.")
            continue
        elif (int(usr) not in user_list):
            print("User not in above list, please try again.")
            continue
        else:
            break

    # Acquire and present selected user stats
    cursor.execute("""SELECT COUNT(*) FROM tweets WHERE writer = ?;""", (usr,))
    num_tweets = cursor.fetchone()[0]
    
    cursor.execute("""SELECT COUNT(*) FROM follows WHERE flwer = ?;""", (usr,))
    num_following = cursor.fetchone()[0]
    
    cursor.execute("""SELECT COUNT(*) FROM follows WHERE flwee = ?;""", (usr,))
    num_followers = cursor.fetchone()[0]
    
    cursor.execute("""SELECT text FROM tweets WHERE writer = ? ORDER BY tdate DESC;""", (usr,))
    recent_tweets = cursor.fetchall()
    
    print(f"Number of tweets: {num_tweets}")
    print(f"Number of users being followed: {num_following}")
    print(f"Number of followers: {num_followers}")
    print("Recent tweets:")

    # Display tweets and provide option to follow or exit
    index = 0
    for tweet in recent_tweets:
        if (index < 3):
            print(tweet[0])
            index += 1
    
    recent_tweets_list = [tweet[0] for tweet in recent_tweets]
    recent_tweets_list = recent_tweets_list[3:]
    
    while (len(recent_tweets_list) > 0):
        choice = input("\nEnter 1 to see more tweets, 2 to follow this user or 3 to exit: ")
        if (choice == '1'):
            if len(recent_tweets_list) > 0:
                for i in range(3):
                    if (len(recent_tweets_list) > i):
                        print (recent_tweets_list[i])
                recent_tweets_list = recent_tweets_list[3:]
        elif (choice == '2'):
            follow_user(True, usr, user_id)
        elif (choice == '3'):
            return


    print("No more tweets to show. \nEnter 1 to follow this user or 2 to exit:")
    choice = input()
    if (choice == '1'):
        follow_user(True, usr, user_id)
    else:
        return


def follow_user(this_user, followers_list, user_id):
    ## Allows user to follow another
    print("****************************************\n")

    # Verifies follow intention and selection
    if (this_user == False):
        choice = input("Press 1 to follow a user or 0 to exit: ")

        if (choice == '0'):
            return

        index = 0
        while(index < 3):
            flwee = input("Enter the user ID of the user from the list to follow: ")
            if (flwee == ''):
                print("Invalid input, please try again.")
                continue
            elif (flwee not in followers_list):
                print("User not in above list, please try again.")
                continue
            else:
                break
            index += 1

    else:
        flwee = followers_list

    mydate = date.today()

    # Record new following relationship if not already present
    cursor.execute("SELECT * FROM follows WHERE flwer=? AND flwee=?", (int(user_id), flwee))
    if cursor.fetchone() is not None:
        print("\nYou are already following this user")
        return

    cursor.execute("""INSERT INTO follows (flwer, flwee, start_date) VALUES (?, ?, ?);""", (int(user_id), flwee, mydate))
    print("Followed successfully")
    connection.commit()

def list_followers(user_id):
    ## List followers of a given user
    print("****************************************\n")
    print("Followers of user with ID " + str(user_id) + ": ")
    
    # Finds and presents followers
    cursor.execute("""SELECT flwer FROM follows WHERE flwee = ?;""", (user_id,))
    
    followers = cursor.fetchall()
    followers_list = []

    for follower in followers:
        print(follower[0]) 
        followers_list.append(follower[0])

    # Provides option to see more follower information
    while(True):     
        choice = input("Press 1 to see more information about a user or 2 to exit: ")
        if (choice == '1'):
            show_user_info(followers_list, user_id)
            break
        elif (choice == '2'):
            break
        else:
            print("Invalid input")
            continue

def exitSafely():
    ## Ensure connection closed before exiting
    connection.close()
    exit()

def main():
    ## Main function to connect to provided database and call driver
    global connection, cursor

    # Finds and connects to database
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = input("Please enter the database path (e.g., './tweets.db'): ")

    if not path:
        path = "./tweets.db"

    custom_definition = False
    if custom_definition:
        define_tables()

    connect(path)
    connection.commit()

    # Optional database query
    debug = False
    if debug:
        cursor.execute("Select * from mentions")
        print(cursor.fetchall())

    # Driver code
    main_screen()

    connection.close()

    return


if __name__ == "__main__":
    main()
