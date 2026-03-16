from werkzeug.security import generate_password_hash

# --- DEFINE YOUR PASSWORDS HERE ---
# Choose simple passwords for your dummy users.
password_for_alice = 'alice123'
password_for_bob = 'bob456'
password_for_admin = 'admin_password' # This will be for your admin user

# --- GENERATE THE HASHES ---
# This creates secure, one-way hashes of the passwords.
hash_alice = generate_password_hash(password_for_alice)
hash_bob = generate_password_hash(password_for_bob)
hash_admin = generate_password_hash(password_for_admin)

# --- PRINT THE RESULTS ---
# Copy the entire output of this script to use in your SQL file.
print("--- COPY THE HASHES BELOW ---")
print(f"Alice's Hash: {hash_alice}")
print(f"Bob's Hash:   {hash_bob}")
print(f"Admin's Hash: {hash_admin}")
print("-----------------------------")
