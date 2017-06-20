# Lightning Payments Draft

This (very draft!) proposal builds on
[bech32 encoding](https://github.com/sipa/bech32/blob/master/bip-witaddr.mediawiki),
while providing a minimal QR-code-ready format for requesting
lightning payments.

Human readable part:
1. Prefix: "ln" + BIP-bech32 currency prefix (eg. lnbc, lntb)
1. (Optional) amount in bitcoin (m/u/n/p accepted here)

And data part:
1. UTC timestamp in seconds-since-Unix-epoch (35 bits)
1. Zero or more tagged parts.
1. Signature (bitcoin-style, of SHA256(SHA256(), plus recovery byte) of above. (520 bits)

Tagged parts are of format:
1. type (5 bits)
1. length (10 bits)
1. data (length x 5 bits)

Currently defined tagged parts are:
1. p: Payment hash (256 bits)
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
   1. fee (64 bits)
   1. ctlv (16 bits)

## Examples (from [examples.sh](examples.sh)):

You can find a [python implementation](lightning-address.py) in this
repository, which produces these (you'll need to `pip install
secp256k1 base58`).  You can feed them back into `lightning-address.py decode`
too:

> ### Please make a donation of any amount using rhash 0001020304050607080900010203040506070809000102030405060708090102 to me @03e7156ae33b0a208d0744199163177e909e80176e55d97a2f221ede0f934dd9ad
> lnbc1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqq7fshvguvjs864g4yj47aedw4y402hdl9g2tqqhyed3nuhr7c908g6uhq9llj7w3s58k3sej3tcg4weqxrxmp3cwxuvy9kfr0uzy8jgpy6uzal
> 
> ### Please send $3 for a cup of coffee to the same peer, within 1 minute
> lnbc2500u1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdq5xysxxatsyp3k7enxv4jsxqzpuazh8qt5w7qeewkmxtv55khqxvdfs9zzradsvj7rcej9knpzdwjykcq8gv4v2dl705pjadhpsc967zhzdpuwn5qzjm0s4hqm2u0vuhhqq7vc09u
> 
> ### Now send $24 for an entire list of things (hashed)
> lnbc20m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsvjfls3ljx9e93jkw0kw40yxn4pevgzflf83qh2852esjddv4xk4z70nehrdcxa4fk0t6hlcc6vrxywke6njenk7yzkzw0quqcwxphkcpvam37w
> 
> ### The same, on testnet, with a fallback address mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP
> lntb20m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsfpp3x9et2e20v6pu37c5d9vax37wxq72un9834d947p45ua8rmrtxlu925gfeun3rsnsj0yvnsk3c2xn8d0py83yv74utuszg6gdzpx8gk8h73yq80pn3dr7hpc2l9vkyftqenn700cq6jnm2t
> 
> ### On mainnet, with fallback address 1RustyRX2oai4EYYDpQGWvEL62BBGqN9T with extra routing info to get to node 029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255
> lnbc20m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsfpp3qjmp7lwpagxun9pygexvgpjdc4jdj85frzjq20q82gphp2nflc7jtzrcazrra7wwgzxqc8u7754cdlpfrmccae92qgzqvzq2ps8pqqqqqqqqqqqq9qqqvtt3eyrxftyx0ncfj64fvtjcpy6xfepmzravcj8pjy7qg5cg366286vfface9ktucg2xzq8zr87rkvsev7h5qyqz4ya4uyz28ruxzugcq2xfueh
> 
> ### On mainnet, with fallback (p2sh) address 3EktnHQD7RiAE6uzMj2ZifT9YgRrkSgzQX
> lnbc20m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfppj3a24vwu6r8ejrss3axul8rxldph2q7z93xufve9n04786ust96l3dj0cp22fw7wyvcjrdjtg57qws9u96n2kv4xf8x9yu2ja6f00vjgp5y4lvj30xxy0duwqgz8yfqypfmxgjksq00galp
> 
> ### On mainnet, with fallback (p2wpkh) address bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4
> lnbc20m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfppqw508d6qejxtdg4y5r3zarvary0c5xw7k2s057u6sfxswv5ysyvmzqemfnxew76stk45gfk0y0azxd8kglwrquhcxcvhww4f7zaxv8kpxwfvxnfdrzu20u56ajnxk3hj3r6p63jqpdsuvna
> 
> ### On mainnet, with fallback (p2wsh) address bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3
> lnbc20m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfp4qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qhkm9qa8yszl8hqzaz9ctqagexxk2l0fyjcy0xhlsaggveqstwmz8rfc3afujc966fgjk47mzg0zzcrcg8zs89722vp2egxja0j3eucsq38r7dh

Feedback welcome!<br>
Rusty.
