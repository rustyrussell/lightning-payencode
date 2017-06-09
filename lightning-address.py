#! /usr/bin/env python3
from lnaddr import lnencode, lndecode, LnAddr
from binascii import hexlify, unhexlify


import argparse


def encode(options):
    """ Convert options into LnAddr and pass it to the encoder
    """
    addr = LnAddr()
    addr.currency = options.currency
    addr.fallback = options.fallback if options.fallback else None
    if options.amount:
        addr.amount = options.amount

    addr.paymenthash = unhexlify(options.paymenthash)

    if options.description:
        addr.tags.append(('d', options.description))
    if options.description_hashed:
        addr.tags.append(('h', options.description_hashed))
    if options.expires:
        addr.tags.append(('x', options.expires))

    if options.fallback:
        addr.tags.append(('f', options.fallback))

    for r in options.route:
        splits = r.split('/')
        assert len(splits) == 4
        addr.tags.append(('r', (
            unhexlify(splits[0]),
            unhexlify(splits[1]),
            int(splits[2]),
            int(splits[3])
        )))
    return lnencode(addr, options.privkey)


def decode(options):
    return lndecode(options.lnaddress)

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
parser_enc.set_defaults(func=encode)

parser_dec.add_argument('lnaddress', help='Address to decode')
parser_dec.add_argument('--rate', type=float, help='Convfersion amount for 1 currency unit')
parser_dec.add_argument('--pubkey', help='Public key for the chanid')
parser_dec.set_defaults(func=decode)

if __name__ == "__main__":
    options = parser.parse_args()
    if not options.subparser_name:
        parser.print_help()
    else:
        print(options.func(options))
