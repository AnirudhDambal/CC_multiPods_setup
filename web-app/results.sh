for i in {1..1000}; do
  curl -s -X GET  http://127.0.0.1:64735/results &
done