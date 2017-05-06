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
1. f: fallback onchain-address.  For bitcoin, this is 5 bits of witness version
	  followed by a witness problem, with witness version 17 meaning p2pkh, 18
	  means p2sh; both are followed by a 20-byte hash value.
1. r: extra routing information.  This should be appended to the route
      to allow routing to non-public nodes; there may be more
	  than one of these.
   1. pubkey (264 bits)
   1. channel id (64 bits)
   1. fee (32 bits)
   1. ctlv (32 bits)

## TODO

1. Don't just encode address string for fallback, but pull it apart,
   check it, and include the RIPEMD160.

## Examples (from [examples.sh](examples.sh)):

You can find a [python implementation](lightning-address.py) in this
repository, which produces these (you'll need to `pip install
secp256k1`).  You can feed them back into `lightning-address.py decode`
too:

> ### Please send 10 satoshi using rhash 0001020304050607080900010203040506070809000102030405060708090102 to me @03e7156ae33b0a208d0744199163177e909e80176e55d97a2f221ede0f934dd9ad
> lnbc10k1qtyxzn4gqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqg732t68jy3vxnx7m24h9aqlnsevyhagcw9a04vkewwp6qkckz5l083g8tm9yesnh3acv23cxxxxrfhrjcsnum7yx0xexetvfc9454r3squgv6zv
> 
> ### Please send $3 for a cup of coffee to the same peer, within 1 minute
> lnbc250m1qtyxzn4gqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqgdq5xysxxatsyp3k7enxv4jsxqz8sfjvapc99hjcj5fperv2s6v2j35s2793a69ycf2j3jthqcqvv5r8q6a24xz88c9r0v2ruf7dz6u7vysdc3t84al2hh3fkw5hh83pphkspat9n00
> 
> ### Now send $24 for an entire list of things (hashed)
> lnbc2g1qtyxzn4sqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqghp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsmquw3qq4ldhyspzz88zqh0zvn8rnga0mr9zlu4sjkkep0psclsqkd4ntkshgn2572havk4a5sc0vq93q7gsh2vclanl34j6twhurwygp3jc6u6
> 
> ### The same, with a fallback address mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP
> lnbc2g1qtyxzn4sqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqgfphd44ny5tst9shgu6td93hv3jkw42yz52vgfe8j7trvdf9sn24v9r5s5qhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqshyz6gctydk089v8ev46st7s7ssau3fv2wx3hxjz7eme5hf64swxptkczwch8cpdku3k8g7q0wen39e3s30lxp9qm75zckfl6f2pzcgqqa6w64a
> 
> ### The same, with extra routing info to get to node 029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255
> lnbc2g1qtyxzn4sqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqgrz0q20q82gphp2nflc7jtzrcazrra7wwgzxqc8u7754cdlpfrmccae92qgzqvzq2ps8pqqqqqq5qqqqqqcfphd44ny5tst9shgu6td93hv3jkw42yz52vgfe8j7trvdf9sn24v9r5s5qhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqspl3rl5843wzskqdtw67zmrt2qm2a7pjpddypzwg4rd0vv6r5umukj8tv22e8vsm8y5wnsw3zh0p486uzayql9wrz47e9axskjd5d04sq7ncfww

Feedback welcome!<br>
Rusty.
