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

## Examples (from [examples.sh](examples.sh)):

You can find a [python implementation](lightning-address.py) in this
repository, which produces these (you'll need to `pip install
secp256k1 base58`).  You can feed them back into `lightning-address.py decode`
too:

> ### Please make a donation of any amount using rhash 0001020304050607080900010203040506070809000102030405060708090102 to me @03e7156ae33b0a208d0744199163177e909e80176e55d97a2f221ede0f934dd9ad
> lnbc1qtyf84fqqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqgj0zqeqgc3rrtqchp8uu9eg8nlk7aqk7vhfjtuflw2lgurylxyywsj4vc6ch9qfhy96nxvz3ncm5lez78mh05vzd4ze058kwfs5fp2pcqcch3ag
> 
> ### Please send $3 for a cup of coffee to the same peer, within 1 minute
> lnbc2500u1qtyf8desqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqgdq5xysxxatsyp3k7enxv4jsxqz8ss8mj6sann5lue9uufceas3xesk0gxfud3w45vc6ntjxmlelz2sy9cvxvdwwn0t0uhll47572vq70jevq43ck00cfyuvkqa0ktlfth0qqh2jwra
> 
> ### Now send $24 for an entire list of things (hashed)
> lnbc20m1qtyf8desqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqghp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqs5xw5cgud4cylk63dwhgzm2cxk0w292zknrx9tgh8wyu4897a54yqqkeslxevdngw7ad2tqmpwd2crz8epan4jp806z8u0ela8x7vaqqpupnmcu
> 
> ### The same, on testnet, with a fallback address mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP
> lntb20m1qtyf8desqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqgfpp3x9et2e20v6pu37c5d9vax37wxq72un98hp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsre7ucjj9363mp350megvxh4nvykaqq5e6l3rj7g3djer9u9w69jxr6ved3qjepaqxdmf2hru3yaxl7rpxh606d5eydzh3neh0f9a32cp2dwaqe
> 
> ### On mainnet, with fallback address 1RustyRX2oai4EYYDpQGWvEL62BBGqN9T with extra routing info to get to node 029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255
> lnbc20m1qtyf8desqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqgrz0q20q82gphp2nflc7jtzrcazrra7wwgzxqc8u7754cdlpfrmccae92qgzqvzq2ps8pqqqqqq5qqqqqqcfpp3qjmp7lwpagxun9pygexvgpjdc4jdj85fhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsft6znxhghr84cqt48jru8x89daa42p0s7jcxxzmx4jrg9y7mcslzn4s8a0nk89hneqdayfu2g4fe08v4aduh27rr28u3vxd443ngzugparh50e
> 
> ### On mainnet, with fallback (p2sh) address 3EktnHQD7RiAE6uzMj2ZifT9YgRrkSgzQX
> lnbc20m1qtyf8desqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqgfppj3a24vwu6r8ejrss3axul8rxldph2q7z9fp0clme7e7mjnlqjd0l2vunv68fy88hq023n8j576dcyt8lctp69ujaepk96npj7ytf65pyanmu7eq9fmuyww6k3lxw3evhrgsj6hmcp2dd3uf
> 
> ### On mainnet, with fallback (p2wpkh) address bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4
> lnbc20m1qtyf8desqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqgfp4qpc2q7pcdrgqpjysxpvxss9gyzsp3zqsaqvxp6qcypuvpgpswrctqkuhgh3w7kkr6cyqzpqx4ek78hjw5gyyygc5qafjythywye3shz5823nru074cjetkqxuz4cjq34yl4vrlx7w4z3gwy9u63s00k4awfqpkwkhfu
> 
> ### On mainnet, with fallback (p2wsh) address bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3
> lnbc20m1qtyf8desqqypqxpq9qcrsszgqqypqxpq9qcrsszgqqypqxpq9qcrsszgpqgfz4qqvq3zyggpuqpgxq5pvrpqqg9r5psgyqrqc23vxszp5tqjyq4zvvpj9gxzg8ssrgcrqvpjzgvqyzpqpsfzyqqpqmpdx7aahjcd57yygn48s9g0kwpmrx8euk8pu0nv6msnhthevd53te0qgyeggnqkj6eqhezzqu7kepgtxxljqujjr597fz3ngm0xngpd04vmh

Feedback welcome!<br>
Rusty.
