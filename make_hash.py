from werkzeug.security import generate_password_hash

password = "12345"

hashed_password = generate_password_hash(password)

print("HASH:")
print(hashed_password)python make_hash.py