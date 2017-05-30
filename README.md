# Lightning Payments Draft

This (very draft!) proposal builds on
[bech32 encoding](https://github.com/sipa/bech32/blob/master/bip-witaddr.mediawiki),
while providing a minimal QR-code-ready format for requesting
lightning payments.

Human readable part:
1. Prefix: "ln" + BIP-bech32 currency prefix (eg. lnbc, lntb)
1. (Optional) amount in bitcoin (m/u/n/p accepted here)

And data part:
1. Version: 0 (5 bits)
1. UTC timestamp in seconds-since-Unix-epoch (35 bits)
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

## Examples (from [examples.sh](examples.sh)):

You can find a [python implementation](lightning-address.py) in this
repository, which produces these (you'll need to `pip install
secp256k1 base58`).  You can feed them back into `lightning-address.py decode`
too:

> ### Please make a donation of any amount using rhash 0001020304050607080900010203040506070809000102030405060708090102 to me @03e7156ae33b0a208d0744199163177e909e80176e55d97a2f221ede0f934dd9ad
> lnbc1qpvj6chqqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypquuvrkdyhszmjzsa95kuw2mpkkzhn3qmewupphyhtk454mlytc0dn9sqd6n39g79aaf27cydcxm9w2378lf3ap6n4a3hd0tjvugq5fhgpm7ghcn
> 
> ### Please send $3 for a cup of coffee to the same peer, within 1 minute
> lnbc2500u1qpvj6chqqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdq5xysxxatsyp3k7enxv4jsxqz8slk6hqew9z5kzxyk33ast248j3ykmu3wncvgtgk0ewf5c6qnhen45vr43fmtzsh02j6ns096tcpfga0yfykc79e5uw3gh5ltr96q00zqppy6lfy
> 
> ### Now send $24 for an entire list of things (hashed)
> lnbc20m1qpvj6chqqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqscpt2ld45dqewrllnmf6hj355nfeypurkr6a2d0neyq2e6g9u6ur9tl7e7drhglfrn9yxk2cdujutuqksx2agqv8mphl0mzjrwm6k59qq2mnedn
> 
> ### The same, on testnet, with a fallback address mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP
> lntb20m1qpvj6chqqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfpp3x9et2e20v6pu37c5d9vax37wxq72un98hp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsqsj75rjv443nrh8gu5xutlyyqyx6ul76m2rx87yxr5gdfagyywn3s6wtpfrl6elncce7rmh6kndvr5nur76w9u7z0k3gq93fyfpu9zqq3jp9as
> 
> ### On mainnet, with fallback address 1RustyRX2oai4EYYDpQGWvEL62BBGqN9T with extra routing info to get to node 029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255
> lnbc20m1qpvj6chqqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqrz0q20q82gphp2nflc7jtzrcazrra7wwgzxqc8u7754cdlpfrmccae92qgzqvzq2ps8pqqqqqq5qqqqqqcfpp3qjmp7lwpagxun9pygexvgpjdc4jdj85fhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqst7xnzx2sl9rkrc5lgzkcdqs57sj0s0vz8z9g2wk4hucfdrtvupkx93wqjcj8lpejzc95k4p4hw0qrfay5x36def3ret6yd9s0vqwtysqm5z5dw
> 
> ### On mainnet, with fallback (p2sh) address 3EktnHQD7RiAE6uzMj2ZifT9YgRrkSgzQX
> lnbc20m1qpvj6chqqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfppj3a24vwu6r8ejrss3axul8rxldph2q7z9nyustv8ulfckvm84tndurwh2knpspl2m7hwqq7xvhr90lmgzgelktr2wgxnsj9fpmk3cs4waekjkzcmtwl36psn22pvp4pvcr2lsjegqq306hp
> 
> ### On mainnet, with fallback (p2wpkh) address bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4
> lnbc20m1qpvjmhmtqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfppqw508d6qejxtdg4y5r3zarvary0c5xw7khjkc5aw8qzadf8rmpcjlk9g6yp0pllmy6tjm2c3jy92dkk7kqvjj5lxr43wuyk7ff9flkhcx69pfrcsp8q7m4j60qfhsrv34fts7wlcqq2h2lk
> 
> ### On mainnet, with fallback (p2wsh) address bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3
> lnbc20m1qpvjmhmtqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfp4qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qh6q0lqzv5q9dtuwtdxuf0p3dg6dsyxyypk2mhxzste4w5r65ergs666us8eggvnx9z8yjx92j3hh593a94q69xtcpx6e0hxmrqsxvyqp6sknfu

Feedback welcome!<br>
Rusty.
