for number in {0..9}
do
    python bin/slave.py juggler slave${number} simple&
done
wait %?slave || while kill %?slave
do
    true;
done
