#! /usr/bin/python3
import argparse
import hashlib
import re
import sys
import time
# Try 'pip3 install secp256k1'
import secp256k1
# Try 'pip3 install base58'
import base58

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

# Encode directly as a big-endian 35-bit number (for timestamps)
def to_u35(val):
    assert val < (1 << 35)
    ret = []
    for i in range(0,7):
        ret.append(val % 32)
        val //= 32
    ret.reverse()
    return ret

# Represent big-endian number with as many 0-31 values as it takes.
def to_5bit(val):
    ret = []
    while val != 0:
        ret.append(val % 32)
        val //= 32
    ret.reverse()
    return ret

base58_prefix_map = { 'bc' : (0, 5),
                      'tb' : (111, 196) }

def is_p2pkh(currency, prefix):
    return prefix == base58_prefix_map[currency][0]

def is_p2sh(currency, prefix):
    return prefix == base58_prefix_map[currency][1]

def from_u32list(l):
    return (l[0] << 24) + (l[1] << 16) + (l[2] << 8) + l[3]

def from_u35(l):
    ret = 0
    for i in range(0,7):
        ret = ret * 32 + l[i]
    return ret

def from_5bit(l):
    total = 0
    for v in l:
        total = total * 32 + v
    return total

def tagged_unconv(char, bits):
    assert len(bits) < (1 << 10)
    return [CHARSET.find(char), len(bits) >> 5, len(bits) & 31] + bits

def tagged(char, l):
    return tagged_unconv(char, convertbits(l, 8, 5))

# Try to pull out tagged data: returns tag, tagged data and remainder.
def pull_tagged(data):
    if len(data) < 3:
        sys.exit("Truncated field")
    length = data[1] * 32 + data[2]
    if length > len(data) - 3:
        sys.exit("Truncated {} field: expected {} values"
                 .format(CHARSET[data[0]], length))
    return (CHARSET[data[0]], data[3:3+length], data[3+length:])

def lnencode(options):
    if options.no_amount:
        amount = ''
    else:
        picobtc = int(options.amount * 10**12)
        # We can only send down to millisatoshi.
        if picobtc % 10:
            sys.exit("Cannot encode {}: too many decimal places"
                     .format(options.amount))
        if picobtc % 10**12 == 0:
            amount = str(picobtc // 10**12)
        elif picobtc % 10**9 == 0:
            amount = str(picobtc // 10**9) + 'm'
        elif picobtc % 10**6 == 0:
            amount = str(picobtc // 10**6) + 'u'
        elif picobtc % 10**3 == 0:
            amount = str(picobtc // 10**3) + 'n'
        else:
            amount = str(picobtc) + 'p'

    hrp = 'ln' + options.currency + amount

    # version, timestamp and paymenthash
    now = int(time.time())
    data = [0] + to_u35(now) + convertbits(bytearray.fromhex(options.paymenthash), 8, 5)

    for r in options.route:
        pubkey,channel,fee,cltv = r.split('/')
        route = bytearray.fromhex(pubkey) + bytearray.fromhex(channel) + u32list(int(fee)) + u32list(int(cltv))
        data = data + tagged('r', route)

    if options.fallback:
        # Fallback parsing is per-currency, by definition.
        if options.currency == 'bc' or options.currency == 'tb':
            fbhrp, witness = bech32_decode(options.fallback)
            if fbhrp:
                if fbhrp != options.currency:
                    sys.exit("Not a bech32 address for this currency")
                wver = witness[0]
                if wver > 16:
                    sys.exit("Invalid witness version {}".format(witness[0]))
                wprog = witness[1:]
            else:
                addr = base58.b58decode_check(options.fallback)
                if is_p2pkh(options.currency, addr[0]):
                    wver = 17
                elif is_p2sh(options.currency, addr[0]):
                    wver = 18
                else:
                    sys.exit("Unknown address type for {}"
                             .format(options.currency))
                wprog = convertbits(addr[1:], 8, 5)
            data = data + tagged_unconv('f', [wver] + wprog)
        # Other currencies here....
        else:
            sys.exit("FIXME: Add support for parsing this currency")
    
    if options.description:
        data = data + tagged('d', [ord(c) for c in options.description])

    if options.expires:
        data = data + tagged_unconv('x', to_5bit(options.expires))
        
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

    m = re.search("[^\d]+", hrp[2:])
    currency = m.group(0)
    print("Currency: {}".format(currency))

    amountstr = hrp[2+m.end():]
    if amountstr != '':
        # Postfix?
        if amountstr.endswith('p'):
            mul = 1
            amountstr = amountstr[:-1]
        elif amountstr.endswith('n'):
            mul = 10**3
            amountstr = amountstr[:-1]
        elif amountstr.endswith('u'):
            mul = 10**6
            amountstr = amountstr[:-1]
        elif amountstr.endswith('m'):
            mul = 10**9
            amountstr = amountstr[:-1]
        picobtc = int(amountstr) * mul
        print("Amount: {}".format(picobtc / 10**12))

        if options.rate:
            print("(Conversion: {})".format(picobtc / 10**12 * float(options.rate)))

    if len(data) < 7 + 52:
        sys.exit("Not long enough to contain timestamp and payment hash")

    tstamp = from_u35(data[:7])
    data = data[7:]
    print("Timestamp: {} ({})".format(tstamp, time.ctime(tstamp)))

    payment_hash = convertbits(data[:52], 5, 8, False)
    assert len(payment_hash) == 32
    print("Payment hash: {}".format(bytearray(payment_hash).hex()))
    data = data[52:]

    while len(data) > 0:
        tag,tagdata,data = pull_tagged(data)
        if tag == 'r':
            tagdata = convertbits(tagdata, 5, 8, False)
            if len(tagdata) != 33 + 8 + 4 + 4:
                sys.exit('Unexpected r tag length {}'.format(len(tagdata)))
            print("Route: {}/{}/{}/{}"
                  .format(bytearray(tagdata[0:33]).hex(),
                          bytearray(tagdata[33:41]).hex(),
                          from_u32list(tagdata[41:45]),
                          from_u32list(tagdata[45:49])))
        elif tag == 'f':
            if currency == 'bc' or currency == 'tb':
                wver = tagdata[0]
                if wver == 17:
                    addr=base58.b58encode_check(bytes([base58_prefix_map[currency][0]]
                                                      + convertbits(tagdata[1:], 5, 8, False)))
                elif wver == 18:
                    addr=base58.b58encode_check(bytes([base58_prefix_map[currency][1]]
                                                      + convertbits(tagdata[1:], 5, 8, False)))
                elif wver <= 16:
                    addr=bech32_encode(currency, tagdata)
                else:
                    sys.exit('Invalid witness version {}'.format(wver))

            # Other currencies here...
            else:
                addr=bytearray(tagdata).hex()
            print("Fallback: {}".format(addr))
        elif tag == 'd':
            tagdata = convertbits(tagdata, 5, 8, False)
            print("Description: {}".format(''.join(chr(c) for c in tagdata)))
        elif tag == 'h':
            tagdata = convertbits(tagdata, 5, 8, False)
            print("Description hash: {}".format(bytearray(tagdata).hex()))
        elif tag == 'x':
            print("Expiry (seconds): {}".format(from_5bit(tagdata)))
        else:
            tagdata = convertbits(tagdata, 5, 8, False)
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
parser_enc.add_argument('--expires', type=int,
                        help='Seconds before offer expires')
parser_enc.add_argument('--no-amount', action="store_true",
                        help="Don't encode amount")
parser_enc.add_argument('amount', type=float, help='Amount in currency')
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
