users = {
    'user1': {'username': 'Mehdi', 'password': '1234'},
    'user2': {'username': 'Bob', 'password': '25'},
    'user3': {'username': 'John', 'password': '35'},
}
for user, info in users.items():
    if info['username'] == 'Mehdi':
        print(info['password'])