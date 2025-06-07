curl http://127.0.0.1:5000/
curl http://127.0.0.1:5001/
ab -n 1000 -c 50 http://127.0.0.1:5000/ > voting-app-benchmark.txt
ab -n 1000 -c 50 http://127.0.0.1:5001/ > result-app-benchmark.txt
docker logs voting-app
docker logs result-app