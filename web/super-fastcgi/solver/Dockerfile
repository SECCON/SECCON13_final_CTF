FROM golang:1.23.6-bookworm

WORKDIR /app

COPY . .

RUN go build -o solve solve.go

CMD ["./solve"]
