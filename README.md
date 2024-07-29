# NetworkProject-Tik-Tac-toe
This project aims to implement the Toe-Tac-Tic game as client-server using a central server to manage users and  Information storage.
This project is a client-side application for a networked Tic-Tac-Toe game, which allows users to register, log in, and play Tic-Tac-Toe with other online users. The application is built using Python's tkinter for the GUI and socket for network communication.
Server.py:
There are 4 main files in this project, each of them and their main functions are explained below:


The server is built using Python's socket and threading libraries and uses JSON files to persist user and game data.
Features

User Registration and Authentication:
Users can register with a unique username and password.
Users can log in and log out.

User Management:
List all online users.

Game Management:
Users can invite others to a game.
Users can accept invitations to start a game.
Users can make moves in a game.
Users can quit a game.

Files
user_db.json: Stores registered users and their hashed passwords.
games_db.json: Stores active games and their states.

Server Setup
To run the server, simply execute the script. The server will start listening for incoming connections on 127.0.0.1:65432.
python tic_tac_toe_server.py
Server Details

User Registration
Action: register
Request:
{
    "action": "register",
    "username": "example_user",
    "password": "example_password"
}
Response:
{
    "status": "success",
    "message": "User registered successfully."
}
Or:
{
    "status": "error",
    "message": "Username already exists."
}

User Login
Action: login
Request:
{
    "action": "login",
    "username": "example_user",
    "password": "example_password"
}
Response:
{
    "status": "success",
    "username": "example_user"
}
Or:
{
    "status": "error",
    "message": "Invalid username or password."
}
User Logout
Action: logout

Request:
{
    "action": "logout"
}
Response:
{
    "status": "success",
    "message": "Logged out successfully."
}
Or:
{
    "status": "error",
    "message": "User not logged in."
}
List Online Users
Action: list_users

Request:
{
    "action": "list_users"
}
Response:
{
    "action": "list_users",
    "users": ["user1", "user2", ...]
}
Invite to Game
Action: invite

Request:
{
    "action": "invite",
    "to_user": "example_user"
}
Response:
{
    "status": "success",
    "message": "Invitation sent."
}
Or:
{
    "status": "error",
    "message": "User is not online."
}
Accept Game Invitation
Action: accept_invite

Request:
json
Copy code
{
    "action": "accept_invite",
    "from_user": "example_user"
}
Response:
{
    "action": "start_game",
    "game_id": 1234,
    "turn": "X"
}
Or:
json
Copy code
{
    "status": "error",
    "message": "User is not online."
}
Make Move
Action: make_move

Request:
{
    "action": "make_move",
    "game_id": 1234,
    "move_index": 0
}
Response:
{
    "status": "error",
    "message": "Not your turn."
}
Or:
{
    "status": "error",
    "message": "Invalid move."
}
Quit Game
Action: quit_game

Request:
{
    "action": "quit_game",
    "game_id": 1234
}
Response:
{
    "status": "success",
    "message": "Game ended."
}

Helper Functions
load_from_json: Loads data from a JSON file.
save_to_json: Saves data to a JSON file.
hash_password: Hashes a password using SHA-256.
get_username_by_conn: Retrieves the username associated with a connection.
generate_game_id: Generates a unique game ID.
send_game_update: Sends the game state update to all users.
Concurrency
The server uses threading to handle multiple clients concurrently. Locks are used to ensure thread-safe access to shared resources like the user database and the active games list.
Error Handling
The server is designed to handle common errors such as invalid actions, invalid moves, and attempts to interact with offline users.


Client.py

Features
User Registration and Login: Users can register with a username and password, which are hashed for security. They can also log in with their credentials.
List Online Users: Logged-in users can view a list of other online users.
Send and Receive Game Invitations: Users can send game invitations to other online users and receive invitations.
Play Tic-Tac-Toe: Once an invitation is accepted, users can play a game of Tic-Tac-Toe.
Real-Time Game Updates: The game board updates in real time, reflecting the current state of the game.
Logout and Quit Game: Users can log out or quit the game at any time.

Classes and Methods
TicTacToeClient
init: Initializes the client, sets up the GUI, and starts a thread to receive data from the server.
create_widgets: Creates the GUI elements for the application.
show_login_frame, show_register_frame, show_main_frame, show_game_frame: Methods to switch between different frames (screens).
connect_to_server: Connects to the server.
receive_data: Listens for and processes data received from the server.
send_request: Sends a request to the server.
hash_password: Hashes a password using SHA-256.
register: Handles user registration.
login: Handles user login.
list_users: Requests the list of online users from the server.
show_online_users: Displays the list of online users.
invite: Opens the invite window to send a game invitation.
view_invitations: Opens the invite window to view received invitations.
make_move: Sends a move to the server.
update_game_state: Updates the game board with the latest game state.
check_game_result: Checks for a win or draw in the game.
quit_game: Quits the current game.
logout: Logs out the user.
InviteWindow
init: Initializes the invite window.
create_widgets: Creates the GUI elements for the invite window.
send_invite: Sends a game invitation.
accept_invite: Accepts a game invitation.

Usage
Start the Application:

Run tic_tac_toe_client.py to start the client application.
python tic_tac_toe_client.py
Register a New User:

Click the "Register" button.
Enter a username and password, then click "Register".
If registration is successful, a success message will be displayed.
Login:

Enter your username and password, then click "Login".
If login is successful, the main menu will be displayed.
List Online Users:

Click "List Online Users" to view a list of users currently online.
Send a Game Invitation:

Click "Invite User".
Select a user from the list and click "Invite".
View and Accept Invitations:

Click "View Invitations" to see received game invitations.
Select an invitation and click "Accept" to start a game.
Play Tic-Tac-Toe:

Click on the buttons in the game board to make a move.
The game state will update in real time.
Quit Game:

Click "Quit Game" to exit the current game.
Logout:

Click "Logout" to log out from the application.
