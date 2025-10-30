from cryptography.fernet import Fernet

# Step 1: Generate a key and save it to a file (run once)
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("Key generated and saved to secret.key")

# Step 2: Load the key from the file
def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()

# Step 3: Encrypt a photo
def encrypt_photo(photo_path, encrypted_path):
    key = load_key()
    fernet = Fernet(key)

    with open(photo_path, "rb") as file:
        original_data = file.read()

    encrypted_data = fernet.encrypt(original_data)

    with open(encrypted_path, "wb") as file:
        file.write(encrypted_data)
    print(f"Photo encrypted and saved as {encrypted_path}")

# Step 4: Decrypt a photo
def decrypt_photo(encrypted_path, decrypted_path):
    key = load_key()
    fernet = Fernet(key)

    with open(encrypted_path, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = fernet.decrypt(encrypted_data)

    with open(decrypted_path, "wb") as file:
        file.write(decrypted_data)
    print(f"Photo decrypted and saved as {decrypted_path}")

# Example usage
if __name__ == "__main__":
    # Generate the key (run this only once, then comment it out)
    generate_key()

    # Encrypt a photo
    encrypt_photo("example.jpg", "encrypted_photo.enc")

    # Decrypt the photo
    decrypt_photo("encrypted_photo.enc", "decrypted_example.jpg")