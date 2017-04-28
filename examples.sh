#! /bin/sh

# Dummy placeholder values
RHASH=0001020304050607080900010203040506070809000102030405060708090102
CHANID=1122334455667788
CONVERSION_RATE=1200

echo '# Please send 10 satoshi using rhash $RHASH to node at channel $CHANID (numerically-lesser end of those peers).'
./lightning-address.py encode 10000 $RHASH $CHANID
echo

echo '# Please send $3 for a cup of coffee to the same peer'
./lightning-address.py encode --description='1 cup coffee' $((3 * 100000000000 / $CONVERSION_RATE)) $RHASH $CHANID
echo

echo '# Now send $24 for an entire list of things (hashed)'
./lightning-address.py encode --description-hashed='One piece of chocolate cake, one icecream cone, one pickle, one slice of swiss cheese, one slice of salami, one lollypop, one piece of cherry pie, one sausage, one cupcake, and one slice of watermelon' $((24 * 100000000000 / $CONVERSION_RATE)) $RHASH $CHANID
echo

# NOTE: Does not implement real fallback format yet!
echo '# The same, with a fallback address mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP'
./lightning-address.py encode --fallback=mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP --description-hashed='One piece of chocolate cake, one icecream cone, one pickle, one slice of swiss cheese, one slice of salami, one lollypop, one piece of cherry pie, one sausage, one cupcake, and one slice of watermelon' $((24 * 100000000000 / $CONVERSION_RATE)) $RHASH $CHANID
echo

echo '# The same, with extra routing info to get to node 029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255'
./lightning-address.py encode --route=029e03a901b85534ff1e92c43c74431f7ce72046060fcf7a95c37e148f78c77255/0102030405060708/20/3 --fallback=mk2QpYatsKicvFVuTAQLBryyccRXMUaGHP --description-hashed='One piece of chocolate cake, one icecream cone, one pickle, one slice of swiss cheese, one slice of salami, one lollypop, one piece of cherry pie, one sausage, one cupcake, and one slice of watermelon' $((24 * 100000000000 / $CONVERSION_RATE)) $RHASH $CHANID
