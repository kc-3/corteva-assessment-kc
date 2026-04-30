docker run --name corteva-pg \
  -e POSTGRES_DB=corteva \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15