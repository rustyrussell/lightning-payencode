#! /bin/sh

# Dummy placeholder values
RHASH=0001020304050607080900010203040506070809000102030405060708090102
CONVERSION_RATE=1200
# Random keypair for testing.
PRIVKEY=e126f68f7eafcc8b74f54d269fe206be715000f94dac067d1c04a8ca3b2db734
PUBKEY=03e7156ae33b0a208d0744199163177e909e80176e55d97a2f221ede0f934dd9ad

echo "### Please send 10 satoshi using rhash $RHASH to me @$PUBKEY"
./lightning-address.py encode 10000 $RHASH $PRIVKEY
echo

echo "### Please send \$3 for a cup of coffee to the same peer, within 1 minute"
./lightning-address.py encode --description='1 cup coffee' $((3 * 100000000000 / $CONVERSION_RATE)) --expires=60 $RHASH $PRIVKEY
echo

echo "### Now send \$24 for an entire list of things (hashed)"
./lightning-address.py encode --description-hashed='One piece of chocolate cake, one icecream cone, one pickle, one slice of swiss cheese, one slice of salami, one lollypop, one piece of cherry pie, one sausage, one cupcake, and one slice of watermelon' $((24 * 100000000000 / $CONVERSION_RATE)) $RHASH $PRIVKEY
echo

echo '### The same, on testnet, with a fallback address mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP'
./lightning-address.py encode --currency=tb --fallback=mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP --description-hashed='One piece of chocolate cake, one icecream cone, one pickle, one slice of swiss cheese, one slice of salami, one lollypop, one piece of cherry pie, one sausage, one cupcake, and one slice of watermelon' $((24 * 100000000000 / $CONVERSION_RATE)) $RHASH $PRIVKEY
echo

echo '### On mainnet, with fallback address 1RustyRX2oai4EYYDpQGWvEL62BBGqN9T with extra routing info to get to node 029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255'
./lightning-address.py encode --route=029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255/0102030405060708/20/3 --fallback=1RustyRX2oai4EYYDpQGWvEL62BBGqN9T --description-hashed='One piece of chocolate cake, one icecream cone, one pickle, one slice of swiss cheese, one slice of salami, one lollypop, one piece of cherry pie, one sausage, one cupcake, and one slice of watermelon' $((24 * 100000000000 / $CONVERSION_RATE)) $RHASH $PRIVKEY
echo

echo '### On mainnet, with fallback (p2sh) address 3EktnHQD7RiAE6uzMj2ZifT9YgRrkSgzQX'
./lightning-address.py encode --fallback=3EktnHQD7RiAE6uzMj2ZifT9YgRrkSgzQX $((24 * 100000000000 / $CONVERSION_RATE)) $RHASH $PRIVKEY
echo

echo '### On mainnet, with fallback (p2wpkh) address bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'
./lightning-address.py encode --fallback=bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4 $((24 * 100000000000 / $CONVERSION_RATE)) $RHASH $PRIVKEY
echo

echo '### On mainnet, with fallback (p2wsh) address bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3'
./lightning-address.py encode --fallback=bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3 $((24 * 100000000000 / $CONVERSION_RATE)) $RHASH $PRIVKEY

