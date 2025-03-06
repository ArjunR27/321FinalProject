import pyotp
import qrcode
import os
from dotenv import load_dotenv

def generate_qr_code(key):
    uri = pyotp.totp.TOTP(key).provisioning_uri(name='Arjun Ranade',
                                                issuer_name='DeviceSecurity App')
    qr = qrcode.QRCode(box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save('totp.png')

def generate_and_save_secret():
    if not os.path.exists('.env'):
        secret = pyotp.random_base32()
        with open('.env', 'w') as file:
            file.write(f"AUTHENTICATOR_SECRET={secret}")
        print("New secret key generated and saved.")
        print('Generating new qr_code for google authenticator app')
        generate_qr_code(secret)
    else:
        print("Secret key already exists. Not generating a new one.")

def verify(encoded_secret):
    totp = pyotp.TOTP(encoded_secret)
    while True: 
        print(totp.verify(input(("Enter the Code : "))))

def main():
    load_dotenv()
    generate_and_save_secret()
    secret = os.getenv('AUTHENTICATOR_SECRET')

    if not secret:
        print("Error: Secret key not found. Check your .env file.")
        return
    verify(secret)


if __name__ == "__main__":
    main()
