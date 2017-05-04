# Lightning Payments Draft

This (very draft!) proposal builds on
[bech32 encoding](https://github.com/sipa/bech32/blob/master/bip-witaddr.mediawiki),
while providing a minimal QR-code-ready format for requesting
lightning payments.

Human readable part:
1. Prefix: "ln" + BIP-bech32 currency prefix (eg. lnbc, lntb)
1. Amount in milli(satoshi) (k/m/g accepted here)

And data part:
1. Version: 0 (5 bits)
1. UTC timestamp in seconds-since-Unix-epoch (32 bits)
1. Payment hash (256 bits)
1. Zero or more tagged parts.
1. Signature (bitcoin-style, of SHA256(SHA256(), plus recovery byte) of above. (520 bits)

Tagged parts are of format:
1. type (5 bits)
1. length (10 bits)
1. data (length x 5 bits)

Currently defined tagged parts are:
1. d: short description of purpose of payment (ASCII).  eg. '1 cup of coffee'
1. h: description of purpose of payment (SHA256).  This is used to commit
   to an associated description which is too long to fit, such as may
   be contained in a web page.
1. x: expiry time in seconds. Default is 3600 (1 hour) if not specified.
1. f: fallback onchain-address.  20 bytes == p2pkh.  21 bytes == p2wpkh, 33 bytes == p2wsh.
1. r: extra routing information.  This should be appended to the route
      to allow routing to non-public nodes; there may be more
	  than one of these.
   1. pubkey (264 bits)
   1. channel id (64 bits)
   1. fee (32 bits)
   1. ctlv (32 bits)

## TODO

1. Implement signatures and checking in the demo code (currently it's 64 zeroes)

1. Don't just encode address string for fallback, but pull it apart,
   check it, and include the RIPEMD160.

## Examples (from [examples.sh](examples.sh)):

You can find a [python implementation](lightning-address.py) in this
repository, which produces these (you'll need to `pip install
secp256k1`).  You can feed them back into `lightning-address.py decode`
too:

> # Please send 10 satoshi using rhash $RHASH to node at channel $CHANID (numerically-lesser end of those peers).
> lnbc10k1qqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqyppzg3ng32kvaugg25s00urer9qtprkzgtu3gx94acw4q7gw0m03rpydlusn72d3lrr4qksuykeal8xlshrjxkdmtmju8cwendjrx0u2u7362my85rsh2chsav63
> 
> # Please send $3 for a cup of coffee to the same peer
> lnbc250m1qqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqyppzg3ng32kvaugdq5xysxxatsyp3k7enxv4jspzwjxkaq4dcvjxtf5ssatd36ldnud5zvwwdzfr048d9mautjynkrx57mcphd4luj3kcj90yf2uytrvqthrcev7r5dp0yqzgw2zmdkwsrpp3m2
> 
> # Now send $24 for an entire list of things (hashed)
> lnbc2g1qqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqyppzg3ng32kvaughp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsuhzprl5clgmzy87w3wrjc8hyy9s5h4u705sklp0ejk74asl0x6k83dcntjqrjks9x4rnln94huk6p46a9a6rns8wyk6cuyztyneu78g4fjzyd
> 
> # The same, with a fallback address mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP
> lnbc2g1qqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqyppzg3ng32kvaugfphd44ny5tst9shgu6td93hv3jkw42yz52vgfe8j7trvdf9sn24v9r5s5qhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs39dnhe3f8xnu86jy2dt3ucgw4w40hz9k6urrymtesqr6xrvr3zaz7gegn0lkfv8kfcp5kmrmk3d4awam8rpn3adzzg7z6j6kqhm29pc0v4836
> 
> # The same, with extra routing info to get to node 029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255
> lnbc2g1qqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqyppzg3ng32kvaugrz0q20q82gphp2nflc7jtzrcazrra7wwgzxqc8u7754cdlpfrmccae92qgzqvzq2ps8pqqqqqq5qqqqqqcfphd44ny5tst9shgu6td93hv3jkw42yz52vgfe8j7trvdf9sn24v9r5s5qhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsl76rvtg46qmutaxm39pejhq0tlc5cq7x2e6ant85e203drl7ctengyfvxx6kjle7rwpry4muhaade589r340ke9kjg4ckwj4vjrnezc5a32gc

Feedback welcome!<br>
Rusty.
