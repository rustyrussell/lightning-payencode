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
> lnbc1qtyk42ssqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqvjknmr2qunez7y07zr2wd259mmzzrewc95sz52l6r3dp390hskeszwlh7czsz2gwx4e3ha2hjf923sdw0l4k97z0tlj8qe033srjs4gp5s8kfs
> 
> ### Please send $3 for a cup of coffee to the same peer, within 1 minute
> lnbc2500u1qtyk42ssqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdq5xysxxatsyp3k7enxv4jsxqz8sgvg68messm5zmn0c906drzz28y5sk43hj3wla62elrh2ynzyn83n9240x5dhyrqyd8uvl0tq2dx52sf9y569nv78tzk7pvlqg5rgjqcpt0atu3
> 
> ### Now send $24 for an entire list of things (hashed)
> lnbc20m1qtyk42ssqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsvvrzv09wvu8zypu4dpe0jzzjtwv22vaumjgf352kxvcgew7z3elp7tc3t0u34xp4lm7yadgdtq6unrsqq63u5r0q26xa2p5z2q6rm7cphd47lr
> 
> ### The same, on testnet, with a fallback address mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP
> lntb20m1qtyk42ssqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfpp3x9et2e20v6pu37c5d9vax37wxq72un98hp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs9watcnvz30tdhklwjjz37lfkvrkp5efkprplf75d7dhkcxce9zurganvqfyh22vj2z5ag7gpvrqyr6q35p92hg56dc0x6wklkj8q8esp48cx3e
> 
> ### On mainnet, with fallback address 1RustyRX2oai4EYYDpQGWvEL62BBGqN9T with extra routing info to get to node 029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255
> lnbc20m1qtyk42ssqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqrz0q20q82gphp2nflc7jtzrcazrra7wwgzxqc8u7754cdlpfrmccae92qgzqvzq2ps8pqqqqqq5qqqqqqcfpp3qjmp7lwpagxun9pygexvgpjdc4jdj85fhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqscyjmukny47rpk3a383h6er7uezsttxshluj8z3a2lgwlq5nymdxn3fl9nrmyc8plkhs529cwm60j0nd8ucxg75stdu44lkm0c8f543qq2lcytr
> 
> ### On mainnet, with fallback (p2sh) address 3EktnHQD7RiAE6uzMj2ZifT9YgRrkSgzQX
> lnbc20m1qtyk42scqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfppj3a24vwu6r8ejrss3axul8rxldph2q7z90hg2u0eenjtz68gjf3fhk265uwmaae3q3g900zk0h7v9xeu2dkt9tj2zwjc9vazevasuzh2kxeq7z82f05xa24ch6a03uy4sd9z24hspcnv2au
> 
> ### On mainnet, with fallback (p2wpkh) address bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4
> lnbc20m1qtyk42scqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfp4qpc2q7pcdrgqpjysxpvxss9gyzsp3zqsaqvxp6qcypuvpgpswrctqp72szmdn96p9hl7z350txyz4j8m4jwkz7ct4pq6z9tqvhn35tz2rx08fvvanktzqhq6yteh95cw43yz2gu0q26xjjh2k2w5auj4zlvsq3h45pp
> 
> ### On mainnet, with fallback (p2wsh) address bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3
> lnbc20m1qtyk42scqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqfz4qqvq3zyggpuqpgxq5pvrpqqg9r5psgyqrqc23vxszp5tqjyq4zvvpj9gxzg8ssrgcrqvpjzgvqyzpqpsfzyqqqwzg25vp40ezmdf42cr89ygy66nlsad3de3aeqja0yygarqu32zsfxupcyq3mcs9kukm7j45xfu55cfzuua20l5ek63xcwpp32me3qqp9keuy2

Feedback welcome!<br>
Rusty.
