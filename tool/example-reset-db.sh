echo DELETE db juggler
restcli http://localhost:5984/juggler -X DELETE
echo couchdb-compose
couchdb-compose push juggler --path composeapp
echo put project
python tool/put.py juggler tool/example_project.yml
echo put order
python tool/put.py juggler tool/example_order.yml --newid order
