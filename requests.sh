for i in {1..1000}; do
  curl -s -X POST -H "Content-Type: application/json" -d '{"candidate":"A"}' http://127.0.0.1:58460/vote  &
done