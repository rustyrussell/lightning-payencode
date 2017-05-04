#! /usr/bin/python3
import argparse
import hashlib
import re
import sys
# Try 'pip3 install secp256k1'
import secp256k1

# All the hard parts stolen from https://github.com/sipa/bech32/blob/master/ref/python/segwit_addr.py:

# Copyright (c) 2017 Pieter Wuille
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Reference implementation for Bech32 and segwit addresses."""


CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def bech32_polymod(values):
    """Internal function that computes the Bech32 checksum."""
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def bech32_hrp_expand(hrp):
    """Expand the HRP into values for checksum computation."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def bech32_verify_checksum(hrp, data):
    """Verify a checksum given HRP and converted data characters."""
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1


def bech32_create_checksum(hrp, data):
    """Compute the checksum values given HRP and data."""
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def bech32_encode(hrp, data):
    """Compute a Bech32 string given HRP and data values."""
    combined = data + bech32_create_checksum(hrp, data)
    return hrp + '1' + ''.join([CHARSET[d] for d in combined])


def bech32_decode(bech):
    """Validate a Bech32 string, and determine HRP and data."""
    if ((any(ord(x) < 33 or ord(x) > 126 for x in bech)) or
            (bech.lower() != bech and bech.upper() != bech)):
        return (None, None)
    bech = bech.lower()
    pos = bech.rfind('1')
    if pos < 1 or pos + 7 > len(bech): #or len(bech) > 90:
        return (None, None)
    if not all(x in CHARSET for x in bech[pos+1:]):
        return (None, None)
    hrp = bech[:pos]
    data = [CHARSET.find(x) for x in bech[pos+1:]]
    if not bech32_verify_checksum(hrp, data):
        return (None, None)
    return (hrp, data[:-6])


def convertbits(data, frombits, tobits, pad=True):
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret


def decode(hrp, addr):
    """Decode a segwit address."""
    hrpgot, data = bech32_decode(addr)
    if hrpgot != hrp:
        return (None, None)
    decoded = convertbits(data[1:], 5, 8, False)
    if decoded is None or len(decoded) < 2 or len(decoded) > 40:
        return (None, None)
    if data[0] > 16:
        return (None, None)
    if data[0] == 0 and len(decoded) != 20 and len(decoded) != 32:
        return (None, None)
    return (data[0], decoded)


def encode(hrp, witver, witprog):
    """Encode a segwit address."""
    ret = bech32_encode(hrp, [witver] + convertbits(witprog, 8, 5))
    assert decode(hrp, ret) is not (None, None)
    return ret

######

# Represent as a big-endian 32-bit number.
def u32list(val):
    assert val < (1 << 32)
    return bytearray([(val >> 24) & 0xff, (val >> 16) & 0xff, (val >> 8) & 0xff, val & 0xff])

def from_u32list(l):
    return (l[0] << 24) + (l[1] << 16) + (l[2] << 8) + l[3]

def tagged(char, l):
    bits=convertbits(l, 8, 5)
    assert len(bits) < (1 << 10)
    return [CHARSET.find(char), len(bits) >> 5, len(bits) & 31] + bits

# Try to pull out tagged data: returns tag, tagged data and remainder.
def pull_tagged(data):
    if len(data) < 3:
        sys.exit("Truncated field")
    length = data[1] * 32 + data[2]
    if length > len(data) - 3:
        sys.exit("Truncated {} field: expected {} values"
                 .format(CHARSET[data[0]], length))
    return (CHARSET[data[0]], convertbits(data[3:3+length], 5, 8, False), data[3+length:])

def lnencode(options):
    # Minimize amounts using postfix:
    if options.amount % 1000000000 == 0:
        amount = str(options.amount // 1000000000) + 'g'
    elif options.amount % 1000000 == 0:
        amount = str(options.amount // 1000000) + 'm'
    elif options.amount % 1000 == 0:
        amount = str(options.amount // 1000) + 'k'
    else:
        amount = str(options.amount)
    
    hrp = 'ln' + options.currency + amount
    
    # version + paymenthash
    data = [0] + convertbits(bytearray.fromhex(options.paymenthash), 8, 5)
    
    for r in options.route:
        pubkey,channel,fee,cltv = r.split('/')
        route = bytearray.fromhex(pubkey) + bytearray.fromhex(channel) + u32list(int(fee)) + u32list(int(cltv))
        data = data + tagged('r', route)

    if options.fallback:
        # FIXME: Take a real address here, and check and strip the checksum & currency.
        data = data + tagged('f', [ord(c) for c in options.fallback])
    
    if options.description:
        data = data + tagged('d', [ord(c) for c in options.description])
    
    if options.description_hashed:
        data = data + tagged('h', hashlib.sha256(options.description_hashed.encode('utf-8')).digest())

    # We actually sign the hrp, then the array of 5-bit values as bytes.
    privkey = secp256k1.PrivateKey(bytes(bytearray.fromhex(options.privkey)))
    sig = privkey.ecdsa_sign_recoverable(bytearray([ord(c) for c in hrp] + data))
    # This doesn't actually serialize, but returns a pair of values :(
    sig,recid = privkey.ecdsa_recoverable_serialize(sig)
    data = data + convertbits(bytes(sig) + bytes([recid]), 8, 5)

    print(bech32_encode(hrp, data))

def lndecode(options):
    hrp, data = bech32_decode(options.lnaddress)
    if not hrp:
        sys.exit("Bad bech32 checksum")

    if not hrp.startswith('ln'):
        sys.exit("Does not start with ln")

    if data[0] != 0:
        sys.exit("Unknown version {}".format(data[0]))
    data = data[1:]

    # Final signature takes 104 bytes (65 bytes base32 encoded)
    if len(data) < 103:
        sys.exit("Too short to contain signature")
    sigdecoded = convertbits(data[-104:], 5, 8, False)
    data = data[:-104]

    pubkey = secp256k1.PublicKey(flags=secp256k1.ALL_FLAGS)
    sig = pubkey.ecdsa_recoverable_deserialize(sigdecoded[0:64], sigdecoded[64])
    pubkey.public_key = pubkey.ecdsa_recover(bytearray([ord(c) for c in hrp] + data), sig)
    print("Signed with public key: {}".format(bytearray(pubkey.serialize()).hex()))
    
    m = re.search("\d+", hrp)
    if not m:
        sys.exit("Does not contain amount")

    print("Currency: {}".format(hrp[2:m.start()]))
    amount=int(m.group(0))
    # Postfix?
    if hrp[m.end():] == 'k':
        amount = amount * 1000
    elif hrp[m.end():] == 'm':
        amount = amount * 1000000
    elif hrp[m.end():] == 'g':
        amount = amount * 1000000000
    elif hrp[m.end():] != '':
        sys.exit("Unknown amount postfix " + hrp[m.end():])

    print("Amount: {}".format(amount))
    if options.rate:
        print("(Conversion: {})".format(amount / 10**11 * float(options.rate)))

    # 32 bytes turns into 52 bytes when base32 encoded.
    if len(data) < 52:
        sys.exit("Not long enough to contain payment hash")

    decoded = convertbits(data[:52], 5, 8, False)
    data = data[52:]
    assert len(decoded) == 32
    print("Payment hash: {}".format(bytearray(decoded).hex()))

    while len(data) > 0:
        tag,tagdata,data = pull_tagged(data)
        if tag == 'r':
            if len(tagdata) != 33 + 8 + 4 + 4:
                sys.exit('Unexpected r tag length {}'.format(len(tagdata)))
            print("Route: {}/{}/{}/{}"
                  .format(bytearray(tagdata[0:33]).hex(),
                          bytearray(tagdata[33:41]).hex(),
                          from_u32list(tagdata[41:45]),
                          from_u32list(tagdata[45:49])))
        elif tag == 'f':
            # FIXME: Format address!
            print("Fallback: {}".format(bytearray(tagdata).hex()))
        elif tag == 'd':
            print("Description: {}".format(''.join(chr(c) for c in tagdata)))
        elif tag == 'h':
            print("Description hash: {}".format(bytearray(tagdata).hex()))
        else:
            print("UNKNOWN TAG {}: {}".format(tag, bytearray(tagdata).hex()))


parser = argparse.ArgumentParser(description='Encode lightning address')
subparsers = parser.add_subparsers(dest='subparser_name',
                                   help='sub-command help')

parser_enc = subparsers.add_parser('encode', help='encode help')
parser_dec = subparsers.add_parser('decode', help='decode help')

parser_enc.add_argument('--currency', default='bc',
                    help="What currency")
parser_enc.add_argument('--route', action='append', default=[],
                        help="Extra route steps of form pubkey/channel/fee/cltv")
parser_enc.add_argument('--fallback',
                        help='Fallback address for onchain payment')
parser_enc.add_argument('--description',
                        help='What is being purchased')
parser_enc.add_argument('--description-hashed',
                        help='What is being purchased (for hashing)')
parser_enc.add_argument('amount', type=int, help='Amount in millisatoshi')
parser_enc.add_argument('paymenthash', help='Payment hash (in hex)')
parser_enc.add_argument('privkey', help='Private key (in hex)')
parser_enc.set_defaults(func=lnencode)

parser_dec.add_argument('lnaddress', help='Address to decode')
parser_dec.add_argument('--rate', type=float, help='Convfersion amount for 1 currency unit')
parser_dec.add_argument('--pubkey', help='Public key for the chanid')
parser_dec.set_defaults(func=lndecode)

options = parser.parse_args()
if not options.subparser_name:
    parser.print_help()
else:
    options.func(options)
