import hashlib

if __name__ == "__main__":
    pass_source = input("Введите пароль: ")
    # Simple hash for testing, not for production
    hashed = hashlib.sha256(pass_source.encode('utf-8')).hexdigest()
    print(hashed)