#! /usr/bin/python3

from hashlib import sha256
from lnaddr import shorten_amount, unshorten_amount, LnAddr, lnencode, lndecode, u5_to_bitarray, bitarray_to_u5
from decimal import Decimal
from binascii import unhexlify, hexlify
from bech32 import bech32_encode, bech32_decode

RHASH=unhexlify('0001020304050607080900010203040506070809000102030405060708090102')
CONVERSION_RATE=1200
PRIVKEY=b'e126f68f7eafcc8b74f54d269fe206be715000f94dac067d1c04a8ca3b2db734'
PUBKEY=b'03e7156ae33b0a208d0744199163177e909e80176e55d97a2f221ede0f934dd9ad'


def test_shorten_amount():
    tests = {
        Decimal(10)/10**12: '10p',
        Decimal(1000)/10**12: '1n',
        Decimal(1200)/10**12: '1200p',
        Decimal(123)/10**6: '123u',
        Decimal(123)/1000: '123m',
        Decimal(3): '3',
    }

    for i, o in tests.items():
        assert shorten_amount(i) == o
        assert unshorten_amount(shorten_amount(i)) == i

def compare(a, b):
    
    if len([t[1] for t in a.tags if t[0] == 'h']) == 1:
        h1 = sha256([t[1] for t in a.tags if t[0] == 'h'][0].encode('utf-8')).digest()
        h2 = [t[1] for t in b.tags if t[0] == 'h'][0]
        assert h1 == h2

    # Need to filter out these, since they are being modified during
    # encoding, i.e., hashed
    a.tags = [t for t in a.tags if t[0] != 'h' and t[0] != 'n']
    b.tags = [t for t in b.tags if t[0] != 'h' and t[0] != 'n']
   
    assert hexlify(b.pubkey.serialize(compressed=True)) == PUBKEY
    assert b.signature != None

    # Unset these, they are generated during encoding/decoding
    b.pubkey = None
    b.signature = None

    assert a.__dict__ == b.__dict__    

def test_roundtrip():
    longdescription = ('One piece of chocolate cake, one icecream cone, one'
                      ' pickle, one slice of swiss cheese, one slice of salami,'
                      ' one lollypop, one piece of cherry pie, one sausage, one'
                      ' cupcake, and one slice of watermelon')
    
    
    tests = [
        LnAddr(RHASH),
        LnAddr(RHASH, amount=Decimal('0.001'),
               tags=[('d', '1 cup coffee'), ('x', 60)]),
        LnAddr(RHASH, amount=Decimal('1'), tags=[('h', longdescription)]),
        LnAddr(RHASH, currency='tb', tags=[('f', 'mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP'), ('h', longdescription)]),
        LnAddr(RHASH, amount=24, tags=[
            ('r', (unhexlify('029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255'), unhexlify('0102030405060708'), 20, 3)), ('f', '1RustyRX2oai4EYYDpQGWvEL62BBGqN9T'), ('h', longdescription)]),
        LnAddr(RHASH, amount=24, tags=[('f', '3EktnHQD7RiAE6uzMj2ZifT9YgRrkSgzQX')]),
        LnAddr(RHASH, amount=24, tags=[('f', 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4')]),
        LnAddr(RHASH, amount=24, tags=[('f', 'bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3')]),
        LnAddr(RHASH, amount=24, tags=[('n', unhexlify(PUBKEY))]),
    ]

    # Roundtrip
    for t in tests:
        o = lndecode(lnencode(t, PRIVKEY))
        compare(t, o)

def test_n_decoding():
    # We flip the signature recovery bit, which would normally give a different
    # pubkey.
    hrp, data = bech32_decode(lnencode(LnAddr(RHASH, amount=24), PRIVKEY))
    databits = u5_to_bitarray(data)
    databits.invert(-1)
    lnaddr = lndecode(bech32_encode(hrp, bitarray_to_u5(databits)))
    assert hexlify(lnaddr.pubkey.serialize(compressed=True)) != PUBKEY

    # But not if we supply expliciy `n` specifier!
    hrp, data = bech32_decode(lnencode(LnAddr(RHASH, amount=24,
                                              tags=[('n', unhexlify(PUBKEY))]),
                                       PRIVKEY))
    databits = u5_to_bitarray(data)
    databits.invert(-1)
    lnaddr = lndecode(bech32_encode(hrp, bitarray_to_u5(databits)))
    assert hexlify(lnaddr.pubkey.serialize(compressed=True)) == PUBKEY

if __name__ == '__main__':
    test_shorten_amount()
    test_roundtrip()
    test_n_decoding()
