package main

import (
	"bufio"
	"encoding/binary"
	"errors"
	"io"
	"math/rand"
	"net"
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

type Client struct {
	conn net.Conn
}

// NewClient creates a new FastCGI client
func NewClient(network, address string) (*Client, error) {
	conn, err := net.Dial(network, address)
	if err != nil {
		return nil, err
	}
	return &Client{conn: conn}, nil
}

// Request represents a FastCGI request
type Request struct {
	Params map[string]string
	Body   []byte
}

// Do sends a FastCGI request and returns the response
func (c *Client) Do(req *Request) ([]byte, error) {
	requestID := uint16(rand.Intn(65535))

	// Begin request
	if err := c.writeBeginRequest(requestID); err != nil {
		return nil, err
	}

	// Send params
	if err := c.writeParams(requestID, req.Params); err != nil {
		return nil, err
	}

	// Send stdin
	if err := c.writeStdin(requestID, req.Body); err != nil {
		return nil, err
	}

	// Read response
	return c.readResponse()
}

func (c *Client) writeBeginRequest(requestID uint16) error {
	h := header{
		Version:       FCGI_VERSION_1,
		Type:          FCGI_BEGIN_REQUEST,
		RequestID:     requestID,
		ContentLength: 8,
		PaddingLength: 0,
	}

	if err := binary.Write(c.conn, binary.BigEndian, h); err != nil {
		return err
	}

	// Role = FCGI_RESPONDER, Flags = 0 (don't keep connection)
	data := []byte{0, FCGI_RESPONDER, 0, 0, 0, 0, 0, 0}
	_, err := c.conn.Write(data)
	return err
}

func (c *Client) writeParams(requestID uint16, params map[string]string) error {
	// Convert params to FastCGI format
	var content []byte
	for key, value := range params {
		content = append(content, encodeLength(uint32(len(key)))...)
		content = append(content, encodeLength(uint32(len(value)))...)
		content = append(content, key...)
		content = append(content, value...)
	}

	// Write params record
	h := header{
		Version:       FCGI_VERSION_1,
		Type:          FCGI_PARAMS,
		RequestID:     requestID,
		ContentLength: uint16(len(content)),
		PaddingLength: 0,
	}

	if err := binary.Write(c.conn, binary.BigEndian, h); err != nil {
		return err
	}

	if len(content) > 0 {
		if _, err := c.conn.Write(content); err != nil {
			return err
		}
	}

	// Write empty params record to signal end
	h.ContentLength = 0
	return binary.Write(c.conn, binary.BigEndian, h)
}

func (c *Client) writeStdin(requestID uint16, content []byte) error {
	contentSize := len(content)

	h := header{
		Version:       FCGI_VERSION_1,
		Type:          FCGI_STDIN,
		RequestID:     requestID,
		ContentLength: uint16(contentSize),
		PaddingLength: 0,
	}

	if err := binary.Write(c.conn, binary.BigEndian, h); err != nil {
		return err
	}

	if _, err := c.conn.Write(content); err != nil {
		return err
	}

	// Write empty stdin record to signal end
	h = header{
		Version:       FCGI_VERSION_1,
		Type:          FCGI_STDIN,
		RequestID:     requestID,
		ContentLength: 0,
		PaddingLength: 0,
	}
	return binary.Write(c.conn, binary.BigEndian, h)
}

func (c *Client) readResponse() ([]byte, error) {
	reader := bufio.NewReader(c.conn)
	var response []byte

	for {
		h := new(header)
		if err := binary.Read(reader, binary.BigEndian, h); err != nil {
			return nil, err
		}

		content := make([]byte, h.ContentLength)
		if _, err := io.ReadFull(reader, content); err != nil {
			return nil, err
		}

		// Skip padding
		if h.PaddingLength > 0 {
			padding := make([]byte, h.PaddingLength)
			if _, err := io.ReadFull(reader, padding); err != nil {
				return nil, err
			}
		}

		switch h.Type {
		case FCGI_STDOUT:
			response = append(response, content...)
		case FCGI_STDERR:
			return nil, errors.New(string(content))
		case FCGI_END_REQUEST:
			return response, nil
		}
	}
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
