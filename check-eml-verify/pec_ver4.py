# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 09:58:20 2023

@author: nannib
"""
import email
import hashlib
from datetime import datetime
from asn1crypto import cms



# these are the components we are going to extract
payload: bytes                      # the original payload
signature: bytes                    # the digital signature
signature_algorithm: str            # the algorithm used to generate the signature
signature_timestamp: datetime       # the signature's timestamp
payload_hash: bytes                 # the payload hash
hash_algorithm: str                 # the algorithm used to calculate the payload hash


# Load the email message in text mode
with open('test.eml', 'r') as f:
    email_message = f.read()

# Parse the email message
msg = email.message_from_string(email_message)
# Find the S/MIME signature attachment
for part in msg.walk():
    if part.get_content_type() == 'application/pkcs7-signature' or part.get_content_type() == "application/x-pkcs7-signature":
        smime_signature = part.get_payload(decode=True)


# Extract the original email message

# Calcolare l'hash solo delle parti del messaggio che non contengono il certificato
hash = hashlib.sha1()
for part in msg.walk():
    if part.get_content_type() != "application/pkcs7-signature" or part.get_content_type() != "application/x-pkcs7-signature":
        #print(repr(part.get_payload(decode=False)).encode())
        hash.update(repr(part.get_payload(decode=True)).encode())

email_hash = hash.hexdigest()
# load the signature in P7 format
# extract the certificater chain
#cert_chain = pkcs7.load_der_pkcs7_certificates(smime_signature)

# extract the needed structures
content_info: cms.ContentInfo = cms.ContentInfo.load(smime_signature)
signed_data: cms.SignedData = content_info['content']
signer_info: cms.SignerInfo = signed_data['signer_infos'][0]

# extract the payload (None if payload is detached)
payload = signed_data['encap_content_info']['content'].native

# extract the remaining components
signature = signer_info['signature'].native
signature_algorithm = signer_info['signature_algorithm']['algorithm'].native
hash_algorithm = signer_info['digest_algorithm']['algorithm'].native
signed_attrs = signer_info['signed_attrs']

for signed_attr in signed_attrs:
    if signed_attr['type'].native:
        if signed_attr['type'].native=='message_digest':
            payload_hash = signed_attr['values'][0].native
        if signed_attr['type'].native=='signing_time':
            signature_timestamp = signed_attr['values'][0].native
#print('The S/MIME signature is valid')
print("timestamp del certificato:",signature_timestamp)

algorithm = signer_info['signature_algorithm'].native
#print(algorithm)
print(hash_algorithm)
# Compare the message digest in the headers with the re-calculated one
print ("hash del certificato:",payload_hash.hex(),"\nhash dell'email     :",email_hash)

if payload_hash.hex() == email_hash:
    print("The email message has not been tampered.")
else:
    print("The email message has been tampered.")


