import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox
import hashlib

HOST = '127.0.0.1'
PORT = 65432

received_invitations = []
logged_in_user = None
online_users = []
game_id = 0
game = True

class TicTacToeClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe Client")
        self.root.configure(bg="#f0f0f0")

        self.create_widgets()
        self.sock = self.connect_to_server()

        threading.Thread(target=self.receive_data, args=(self.sock,), daemon=True).start()

    def create_widgets(self):
        self.login_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.register_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.game_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)

        # Login Frame
        self.login_label = tk.Label(self.login_frame, text="Login", font=("Arial", 18), bg="#f0f0f0")
        self.login_label.pack(pady=5)

        self.login_username_label = tk.Label(self.login_frame, text="Username:", font=("Arial", 12), bg="#f0f0f0")
        self.login_username_label.pack(pady=5)
        self.login_username_entry = tk.Entry(self.login_frame, font=("Arial", 12), width=30)
        self.login_username_entry.pack(pady=5)

        self.login_password_label = tk.Label(self.login_frame, text="Password:", font=("Arial", 12), bg="#f0f0f0")
        self.login_password_label.pack(pady=5)
        self.login_password_entry = tk.Entry(self.login_frame, show='*', font=("Arial", 12), width=30)
        self.login_password_entry.pack(pady=5)

        self.login_button = tk.Button(self.login_frame, text="Login", font=("Arial", 12), command=self.login, bg="#4CAF50", fg="white")
        self.login_button.pack(pady=10)
        self.register_button = tk.Button(self.login_frame, text="Register", font=("Arial", 12), command=self.show_register_frame, bg="#2196F3", fg="white")
        self.register_button.pack(pady=5)

        # Register Frame
        self.register_label = tk.Label(self.register_frame, text="Register", font=("Arial", 18), bg="#f0f0f0")
        self.register_label.pack(pady=5)

        self.register_username_label = tk.Label(self.register_frame, text="Username:", font=("Arial", 12), bg="#f0f0f0")
        self.register_username_label.pack(pady=5)
        self.register_username_entry = tk.Entry(self.register_frame, font=("Arial", 12), width=30)
        self.register_username_entry.pack(pady=5)

        self.register_password_label = tk.Label(self.register_frame, text="Password:", font=("Arial", 12), bg="#f0f0f0")
        self.register_password_label.pack(pady=5)
        self.register_password_entry = tk.Entry(self.register_frame, show='*', font=("Arial", 12), width=30)
        self.register_password_entry.pack(pady=5)

        self.register_button = tk.Button(self.register_frame, text="Register", font=("Arial", 12), command=self.register, bg="#4CAF50", fg="white")
        self.register_button.pack(pady=10)
        self.back_to_login_button = tk.Button(self.register_frame, text="Back to Login", font=("Arial", 12), command=self.show_login_frame, bg="#2196F3", fg="white")
        self.back_to_login_button.pack(pady=5)

        # Main Frame
        self.main_label = tk.Label(self.main_frame, text="Welcome to Tic-Tac-Toe!", font=("Arial", 18), bg="#f0f0f0")
        self.main_label.pack(pady=10)

        self.list_users_button = tk.Button(self.main_frame, text="List Online Users", font=("Arial", 12), command=self.list_users, bg="#4CAF50", fg="white")
        self.list_users_button.pack(pady=5)

        self.invite_button = tk.Button(self.main_frame, text="Invite User", font=("Arial", 12), command=self.invite, bg="#4CAF50", fg="white")
        self.invite_button.pack(pady=5)

        self.view_invitations_button = tk.Button(self.main_frame, text="View Invitations", font=("Arial", 12), command=self.view_invitations, bg="#4CAF50", fg="white")
        self.view_invitations_button.pack(pady=5)

        self.logout_button = tk.Button(self.main_frame, text="Logout", font=("Arial", 12), command=self.logout, bg="#f44336", fg="white")
        self.logout_button.pack(pady=5)

        # Game Frame
        self.board_buttons = []
        for i in range(9):
            button = tk.Button(self.game_frame, text=' ', font='Arial 20', width=5, height=2, command=lambda i=i: self.make_move(i), bg="#ffffff", relief="ridge")
            button.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.board_buttons.append(button)

        self.quit_game_button = tk.Button(self.game_frame, text="Quit Game", font=("Arial", 12), command=self.quit_game, bg="#f44336", fg="white")
        self.quit_game_button.grid(row=3, column=0, columnspan=3, pady=10)

        self.show_login_frame()

    def show_login_frame(self):
        self.register_frame.pack_forget()
        self.main_frame.pack_forget()
        self.game_frame.pack_forget()
        self.login_frame.pack()

    def show_register_frame(self):
        self.login_frame.pack_forget()
        self.main_frame.pack_forget()
        self.game_frame.pack_forget()
        self.register_frame.pack()

    def show_main_frame(self):
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.game_frame.pack_forget()
        self.main_frame.pack()

    def show_game_frame(self):
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.main_frame.pack_forget()
        self.game_frame.pack()

    def connect_to_server(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            self.show_login_frame()
            return sock
        except Exception as e:
            messagebox.showerror("Error", f"Error connecting to server: {e}")

    def receive_data(self, sock):
        global online_users, received_invitations, game_id, game
        while True:
            try:
                data = sock.recv(1024).decode()
                if data:
                    response = json.loads(data)
                    if 'action' in response:
                        if response['action'] == 'invite':
                            messagebox.showinfo("Invitation", f"Invitation received from {response['from_user']}.")
                            received_invitations.append(response['from_user'])
                        elif response['action'] == 'start_game':
                            game_id = response['game_id']
                            game = False
                            self.show_game_frame()
                        elif response['action'] == 'update_game':
                            game_state = response['game_state']
                            self.update_game_state(game_state)
                        elif response['action'] == 'list_users':
                            online_users = response['users']
                            self.show_online_users()
                    else:
                        if response['status'] == 'error':
                            messagebox.showerror("Error", response['message'])
                        elif response['status'] == 'success':
                            if 'message' in response:
                                messagebox.showinfo("Success", response['message'])
                            if 'username' in response:
                                global logged_in_user
                                logged_in_user = response['username']
                                self.show_main_frame()
            except Exception as e:
                messagebox.showerror("Error", f"Error receiving data: {e}")
                break

    def send_request(self, request):
        try:
            self.sock.send(json.dumps(request).encode())
        except Exception as e:
            messagebox.showerror("Error", f"Error sending request: {e}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self):
        username = self.register_username_entry.get()
        password = self.hash_password(self.register_password_entry.get())
        if username and password:
            request = {
                'action': 'register',
                'username': username,
                'password': password
            }
            self.send_request(request)
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")

    def login(self):
        username = self.login_username_entry.get()
        password = self.hash_password(self.login_password_entry.get())
        if username and password:
            request = {
                'action': 'login',
                'username': username,
                'password': password
            }
            self.send_request(request)
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")

    def list_users(self):
        if logged_in_user:
            request = {'action': 'list_users'}
            self.send_request(request)
        else:
            messagebox.showwarning("Login Error", "Please login first.")

    def show_online_users(self):
        if online_users:
            online_users_str = "\n".join(online_users)
            messagebox.showinfo("Online Users", f"Online users:\n{online_users_str}")
        else:
            messagebox.showinfo("Online Users", "No users are online.")

    def invite(self):
        if logged_in_user:
            if not online_users:
                messagebox.showinfo("No Users", "No users are online.")
                return
            InviteWindow(self.root, self.sock, online_users)
        else:
            messagebox.showwarning("Login Error", "Please login first.")

    def view_invitations(self):
        if received_invitations:
            InviteWindow(self.root, self.sock, received_invitations, view_mode=True)
        else:
            messagebox.showinfo("No Invitations", "No invitations received.")

    def make_move(self, index):
        if game_id:
            request = {
                'action': 'make_move',
                'game_id': game_id,
                'move_index': index
            }
            self.send_request(request)

    def update_game_state(self, game_state):  # baraye beroz resani vaziyat bazi 
        for i in range(9):
            self.board_buttons[i].config(text=game_state[i])
        result = self.check_game_result(game_state)
        if result:
            messagebox.showinfo("Game Over", result)
            self.quit_game_button.config(state='normal')
            self.quit_game_button.config(text="Back to Menu", command=self.back_to_menu)
        else:
            self.quit_game_button.config(state='disabled')

    def back_to_menu(self):
        global game_id, game
        game_id = 0
        game = True
        self.show_main_frame()

    def check_game_result(self, board):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        for combo in winning_combinations:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
                return f"{board[combo[0]]} wins!"
        if ' ' not in board:
            return "It's a draw!"
        return None

    def quit_game(self):
        global game_id, game
        if game_id:
            request = {'action': 'quit_game', 'game_id': game_id}
            self.send_request(request)
            game_id = 0
            game = True
            self.show_main_frame()

    def logout(self):
        global logged_in_user
        if logged_in_user:
            request = {'action': 'logout'}
            self.send_request(request)
            logged_in_user = None
            self.show_login_frame()

class InviteWindow:
    def __init__(self, parent, sock, users, view_mode=False):
        self.window = tk.Toplevel(parent)
        self.sock = sock
        self.users = users
        self.view_mode = view_mode

        self.window.title("Invitations" if view_mode else "Invite User")
        self.create_widgets()

    def create_widgets(self):
        self.listbox = tk.Listbox(self.window, font=("Arial", 12), width=30, height=10)
        self.listbox.pack(pady=10)
        for user in self.users:
            self.listbox.insert(tk.END, user)

        if not self.view_mode:
            self.invite_button = tk.Button(self.window, text="Invite", font=("Arial", 12), command=self.send_invite, bg="#4CAF50", fg="white")
            self.invite_button.pack(pady=5)
        else:
            self.accept_button = tk.Button(self.window, text="Accept", font=("Arial", 12), command=self.accept_invite, bg="#4CAF50", fg="white")
            self.accept_button.pack(pady=5)

    def send_invite(self):
        selected_user = self.listbox.get(tk.ACTIVE)
        if selected_user:
            request = {'action': 'invite', 'to_user': selected_user}
            self.sock.send(json.dumps(request).encode())
            self.window.destroy()

    def accept_invite(self):
        selected_user = self.listbox.get(tk.ACTIVE)
        if selected_user:
            request = {'action': 'accept_invite', 'from_user': selected_user}
            self.sock.send(json.dumps(request).encode())
            self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client = TicTacToeClient(root)
    root.mainloop()
