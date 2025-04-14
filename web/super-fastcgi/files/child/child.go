package main

import (
	"bufio"
	"encoding/binary"
	"fmt"
	"io"
	"log/slog"
	"net"
	"os"
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

// FastCGIChild represents a FastCGI process that handles requests
type FastCGIChild struct {
	params map[string]string
	body   []byte
}

func handleConnection(conn net.Conn) {
	defer conn.Close()

	reader := bufio.NewReader(conn)

	// Read FastCGI records
	params := make(map[string]string)
	var body []byte

	for {
		h := &header{}
		if err := binary.Read(reader, binary.BigEndian, h); err != nil {
			if err != io.EOF {
				slog.Error("Error reading header", "error", err)
			}
			return
		}

		slog.Debug("Header", "header", h)

		content := make([]byte, h.ContentLength)
		if _, err := io.ReadFull(reader, content); err != nil {
			slog.Error("Error reading content", "error", err)
			return
		}

		slog.Debug("Content", "content", string(content))

		// Skip padding
		if h.PaddingLength > 0 {
			padding := make([]byte, h.PaddingLength)
			if _, err := io.ReadFull(reader, padding); err != nil {
				slog.Error("Error reading padding", "error", err)
				return
			}
		}

		switch h.Type {
		case FCGI_BEGIN_REQUEST:
			// Just acknowledge the begin request
			continue

		case FCGI_PARAMS:
			if h.ContentLength == 0 {
				// Empty PARAMS record signals end of params
				continue
			}
			// Parse FastCGI params
			pos := 0
			for pos < len(content) {
				nameLen, paramPos := readLength(content, pos)
				valueLen, paramPos := readLength(content, paramPos)
				if paramPos+int(nameLen)+int(valueLen) > len(content) {
					break
				}
				name := string(content[paramPos : paramPos+int(nameLen)])
				value := string(content[paramPos+int(nameLen) : paramPos+int(nameLen)+int(valueLen)])
				params[name] = value
				pos = paramPos + int(nameLen) + int(valueLen)
			}

		case FCGI_STDIN:
			if h.ContentLength == 0 {
				// Empty STDIN record signals end of request
				sendResponse(conn, h.RequestID, params, body)
				continue
			}
			body = append(body, content...)
		}
	}
}

func sendResponse(conn net.Conn, requestID uint16, params map[string]string, body []byte) {
	response := handleRequest(params, body)

	// Write STDOUT record
	writeRecord(conn, FCGI_STDOUT, requestID, []byte(response))
	// Empty STDOUT to signal end
	writeRecord(conn, FCGI_STDOUT, requestID, nil)

	// Write END_REQUEST record
	endRequest := make([]byte, 8)
	writeRecord(conn, FCGI_END_REQUEST, requestID, endRequest)
}

func handleRequest(params map[string]string, body []byte) string {

	if params["HTTP_GIVEMEFLAG"] == "true" {
		return "Content-type: text/plain\r\n\r\nOh, you want the flag? Here you go: " + os.Getenv("FLAG")
	}

	response := fmt.Sprintf("Content-type: text/plain\r\n\r\nReceived FastCGI Request\n\nParams:\n")
	for key, value := range params {
		response += fmt.Sprintf("%s: %s\n", key, value)
	}
	response += fmt.Sprintf("\nBody length: %d\n", len(body))

	return response
}

func writeRecord(conn net.Conn, recordType uint8, requestID uint16, content []byte) {
	h := header{
		Version:       FCGI_VERSION_1,
		Type:          recordType,
		RequestID:     requestID,
		ContentLength: uint16(len(content)),
		PaddingLength: 0,
	}

	binary.Write(conn, binary.BigEndian, h)
	if len(content) > 0 {
		conn.Write(content)
	}
}

func readLength(content []byte, pos int) (uint32, int) {
	if pos >= len(content) {
		return 0, pos
	}
	if content[pos]>>7 == 0 {
		// Single byte length
		return uint32(content[pos]), pos + 1
	}
	// Four byte length
	if pos+4 > len(content) {
		return 0, pos
	}
	length := uint32(content[pos]&0x7f)<<24 |
		uint32(content[pos+1])<<16 |
		uint32(content[pos+2])<<8 |
		uint32(content[pos+3])
	return length, pos + 4
}

// Starts listening for FastCGI requests on port 9000
func main() {
	// Enable debug logging
	// slog.SetDefault(slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelDebug})))

	listener, err := net.Listen("tcp", ":9000")
	if err != nil {
		slog.Error("failed to start server", "error", err)
	}
	defer listener.Close()

	slog.Info("FastCGI server listening on :9000")

	for {
		conn, err := listener.Accept()
		if err != nil {
			slog.Error("Error accepting connection", "error", err)
			continue
		}

		go handleConnection(conn)
	}
}
