import socket
import threading
import json
import os
import random
import hashlib

HOST = '127.0.0.1'
PORT = 65432

USER_DB_FILE = "user_db.json"
GAMES_DB_FILE = "games_db.json"

online_users = {}
active_games = {}

user_db_lock = threading.Lock()
active_games_lock = threading.Lock()

def load_from_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}

def save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def handle_client(conn, addr):
    global online_users, active_games

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            request = json.loads(data)

            if request['action'] == 'register':
                username = request['username']
                password = request['password']
                hashed_password = hash_password(password)
                with user_db_lock:
                    user_db = load_from_json(USER_DB_FILE)
                    if username in user_db:
                        response = {'status': 'error', 'message': 'Username already exists.'}
                    else:
                        user_db[username] = hashed_password
                        save_to_json(user_db, USER_DB_FILE)
                        response = {'status': 'success', 'message': 'User registered successfully.'}
            elif request['action'] == 'login':
                username = request['username']
                password = request['password']
                hashed_password = hash_password(password)
                with user_db_lock:
                    user_db = load_from_json(USER_DB_FILE)
                    if username in user_db and user_db[username] == hashed_password:
                        online_users[username] = conn
                        response = {'status': 'success', 'username': username}
                    else:
                        response = {'status': 'error', 'message': 'Invalid username or password.'}
            elif request['action'] == 'logout':
                username = get_username_by_conn(conn)
                if username:
                    del online_users[username]
                    response = {'status': 'success', 'message': 'Logged out successfully.'}
                else:
                    response = {'status': 'error', 'message': 'User not logged in.'}
            elif request['action'] == 'list_users':
                users_list = list(online_users.keys())
                response = {'action': 'list_users', 'users': users_list}
            elif request['action'] == 'invite':
                to_user = request['to_user']
                from_user = get_username_by_conn(conn)
                if to_user in online_users:
                    invite_request = {'action': 'invite', 'from_user': from_user}
                    online_users[to_user].send(json.dumps(invite_request).encode())
                    response = {'status': 'success', 'message': 'Invitation sent.'}
                else:
                    response = {'status': 'error', 'message': 'User is not online.'}
            elif request['action'] == 'accept_invite':
                from_user = request['from_user']
                to_user = get_username_by_conn(conn)
                if from_user in online_users:
                    game_id = generate_game_id()
                    active_games[game_id] = {'state': [' '] * 9, 'turn': 'X', 'players': {from_user: 'X', to_user: 'O'}}
                    save_to_json(active_games, GAMES_DB_FILE)

                    start_game_request = {'action': 'start_game', 'game_id': game_id, 'turn': 'X'}
                    online_users[from_user].send(json.dumps(start_game_request).encode())
                    online_users[to_user].send(json.dumps(start_game_request).encode())
                    response = None
                else:
                    response = {'status': 'error', 'message': 'User is not online.'}
            elif request['action'] == 'make_move':
                game_id = request['game_id']
                move_index = request['move_index']
                with active_games_lock:
                    if game_id in active_games and active_games[game_id]['state'][move_index] == ' ':
                        username = get_username_by_conn(conn)
                        if active_games[game_id]['players'][username] == active_games[game_id]['turn']:
                            player = active_games[game_id]['players'][username]
                            active_games[game_id]['state'][move_index] = player
                            active_games[game_id]['turn'] = 'O' if player == 'X' else 'X'
                            save_to_json(active_games, GAMES_DB_FILE)

                            game_state = active_games[game_id]['state']
                            game_update = {'action': 'update_game', 'game_state': game_state, 'turn': active_games[game_id]['turn']}
                            send_game_update(game_id, game_update)
                            response = None
                        else:
                            response = {'status': 'error', 'message': 'Not your turn.'}
                    else:
                        response = {'status': 'error', 'message': 'Invalid move.'}
            elif request['action'] == 'quit_game':
                game_id = request['game_id']
                with active_games_lock:
                    if game_id in active_games:
                        del active_games[game_id]
                        save_to_json(active_games, GAMES_DB_FILE)
                response = {'status': 'success', 'message': 'Game ended.'}

            if response:
                conn.send(json.dumps(response).encode())
        except Exception as e:
            break

    conn.close()

def get_username_by_conn(conn):
    for username, connection in online_users.items():
        if connection == conn:
            return username
    return None

def generate_game_id():
    return random.randint(1000, 9999)

def get_game_turn(game_id):
    game_state = active_games[game_id]
    x_count = game_state.count('X')
    o_count = game_state.count('O')
    return 'X' if x_count <= o_count else 'O'

def send_game_update(game_id, game_update):
    for user, conn in online_users.items():
        conn.send(json.dumps(game_update).encode())

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server started on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
