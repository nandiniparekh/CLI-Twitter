# More detail of any AI tool used, including the name, URL, all the input given and all the output received.  

ChatGPT, https://chat.openai.com/

## Kendrick:

Input: Write a basic command line interface in python to navigate through the options in the specifications detailed below:
Provided specifications from assignment specification, from Login Screen to System Functionalities

Output:
registered_users = {
    'usr1': 'pwd1',
    'usr2': 'pwd2'
}

def main_screen():
    print("Welcome to the Twitter-like system!")
    print("1. Log in")
    print("2. Sign up")
    print("3. Exit")
    choice = input("Please enter your choice: ")

    if choice == '1':
        user_id = input("Enter your user ID: ")
        password = input("Enter your password: ")
        if user_id in registered_users and registered_users[user_id] == password:
            # Call function to list tweets and perform other actions for registered users
            list_tweets(user_id)
        else:
            print("Invalid credentials. Please try again.")
            main_screen()
    elif choice == '2':
        # Call function for user signup
        sign_up()
    elif choice == '3':
        exit()
    else:
        print("Invalid choice. Please try again.")
        main_screen()

def list_tweets(user_id):
    # Function to list tweets and perform other actions for registered users
    print(f"Listing tweets for user {user_id}...")
    # Additional functionalities for listing tweets

def sign_up():
    # Function for user signup
    print("User sign-up")
    # Additional functionalities for user signup

#Driver code
main_screen()

## Noor
ChatGPT used for generating dummy records for Users table for testing purposes

prompt: 
users(usr,pwd, name,email,city,timezone)

Search for users. The user should be able to enter a keyword and the system should retrieve all users whose names or cities contain the keyword.
 The result would be sorted as follows: first, all users whose name match the keyword would be listed and these users would be sorted in an ascending 
 order of name length. This would be followed by the list of users whose city but not name match the keyword and this result would be sorted in an 
 ascending order of city length. If there are more than 5 matching users, only 5 would be shown and the user would be given an option to see more but 
 again 5 at a time. The user should be able to select a user and see more information about him/her including the number of tweets, the number of 
 users being followed, the number of followers and up to 3 most recent tweets. The user should be given the option to follow the user or see more tweets.
add records into the user table (only integers) in order to cover all these requirements


response:
To cover these requirements, you'll need a mix of users whose names and cities contain common and unique keywords. Below are sample records that should 
help you test the search functionality effectively:
INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (1, 'pass123', 'Alice', 'alice@email.com', 'Wonderland', 'UTC-5');
INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (2, 'pass123', 'Bob', 'bob@email.com', 'Springfield', 'UTC-6');
INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (3, 'pass123', 'Charlie', 'charlie@email.com', 'Metropolis', 'UTC-5');
INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (4, 'pass123', 'Diana', 'diana@email.com', 'Gotham', 'UTC-4');
INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (5, 'pass123', 'Edward', 'edward@email.com', 'Forks', 'UTC-7');
INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (6, 'pass123', 'Fiona', 'fiona@email.com', 'Magnolia', 'UTC-5');
INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (7, 'pass123', 'Gregor', 'gregor@email.com', 'Themyscira', 'UTC+3');
INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (8, 'pass123', 'Maria', 'maria@email.com', 'Kingston', 'UTC-5');
INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (9, 'pass123', 'Harry', 'harry@email.com', 'Wonderland', 'UTC-5');
INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (10, 'pass123', 'Irene', 'irene@email.com', 'Wonderland', 'UTC-5');



prompt: 
create table tweets (
  tid	      int,
  writer      int,
  tdate       date,
  text        text,
  replyto     int,
  primary key (tid),
  foreign key (writer) references users,
  foreign key (replyto) references tweets
);

can you also insert a few records into tweets based on the users table

response:
Certainly! Here are some SQL INSERT statements for the tweets table based on the users table records I provided earlier. These will populate the tweets table
 with some sample data:

INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (1, 1, '2023-11-01', 'Just discovered a new type of tea in Wonderland! #adventure', NULL);
INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (2, 2, '2023-10-30', 'Does anyone else think Springfield has the best donuts? #foodie', NULL);
INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (3, 3, '2023-11-02', 'Metropolis has never looked better from the sky! #travel', NULL);
INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (4, 4, '2023-11-03', 'Another night of crime fighting in Gotham. #heroLife', NULL);
INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (5, 5, '2023-10-28', 'Exploring the forests in Forks. #nature', NULL);
INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (6, 1, '2023-11-04', 'Anyone wants to join me for a tea party? #Wonderland', NULL);
INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (7, 6, '2023-10-29', 'Found a new spell book today! #magic', NULL);
INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (8, 7, '2023-11-01', 'A strange transformation occurred today... #mystery', NULL);
INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (9, 8, '2023-11-02', 'Looking forward to the music festival in Kingston! #festival', NULL);
INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (10, 1, '2023-10-31', 'Happy Halloween from Wonderland! #Halloween', NULL);


INSERT INTO follows (flwer, flwee, start_date) VALUES
(1, 2, '2023-01-15'),
(1, 3, '2023-01-20'),
(2, 1, '2023-02-05'),
(2, 3, '2023-02-07'),
(3, 1, '2023-03-01'),
(3, 2, '2023-03-11');



prompt: 
*table specs*
create record entries for these tables (relating to the previous tables as well) for testing purposes

response:
Below are some sample records for each of the new tables you've created, with the assumption that they correspond to the data already in the users and tweets tables. The data entries will be formatted for SQL insertion.
-- hashtags
INSERT INTO hashtags (term) VALUES
('Python'),
('AI'),
('MachineLearning'),
('DataScience'),
('OpenAI');

-- mentions
INSERT INTO mentions (tid, term) VALUES
(1, 'Python'),
(2, 'AI'),
(3, 'MachineLearning'),
(1, 'DataScience'),
(2, 'OpenAI');

-- retweets
INSERT INTO retweets (usr, tid, rdate) VALUES
(1, 2, '2023-10-05'),
(2, 1, '2023-10-06'),
(3, 3, '2023-10-07'),
(4, 2, '2023-10-08'),
(5, 1, '2023-10-09');

-- lists
INSERT INTO lists (lname, owner) VALUES
('Tech Enthusiasts', 1),
('AI Researchers', 2),
('Python Developers', 3),
('Data Scientists', 4),
('OpenAI Fans', 5);

-- includes
INSERT INTO includes (lname, member) VALUES
('Tech Enthusiasts', 3),
('AI Researchers', 4),
('Python Developers', 5),
('Data Scientists', 1),
('OpenAI Fans', 2);