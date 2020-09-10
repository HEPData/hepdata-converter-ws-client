docker run -d -p 0.0.0.0:8945:5000 --name hepdata-converter-ws-tests hepdata/hepdata-converter-ws
sleep 2
coverage run -m unittest discover hepdata_converter_ws_client/testsuite 'test_*'
docker stop hepdata-converter-ws-tests
docker container rm hepdata-converter-ws-tests
