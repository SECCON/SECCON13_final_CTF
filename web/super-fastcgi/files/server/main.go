package main

import (
	"fmt"
	"io"
	"log/slog"
	"net"
	"net/http"
	"strconv"
	"strings"
)

type FastCGIServer struct {
	// FastCGI application address (e.g., "127.0.0.1:9000")
	FcgiAddr string
}

func NewFastCGIServer(fcgiAddr string) *FastCGIServer {
	return &FastCGIServer{
		FcgiAddr: fcgiAddr,
	}
}

func (s *FastCGIServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	slog.Debug("ServeHTTP", "request", r)

	if r.Header.Get("Givemeflag") != "" {
		w.Header().Set("Content-Type", "text/plain")
		w.WriteHeader(http.StatusForbidden)
		w.Write([]byte("You are not allowed to access this resource"))
		return
	}

	// Create FastCGI client
	client, err := NewClient("tcp", s.FcgiAddr)
	if err != nil {
		http.Error(w, "Failed to connect to FastCGI application", http.StatusBadGateway)
		slog.Error("FastCGI connection error", "error", err)
		return
	}

	// Read request body
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusInternalServerError)
		return
	}

	// Build FastCGI parameters
	params := make(map[string]string)

	// Script filename
	scriptName := r.URL.Path
	params["SCRIPT_FILENAME"] = scriptName
	params["SCRIPT_NAME"] = r.URL.Path

	// Request method and URI
	params["REQUEST_METHOD"] = r.Method
	params["REQUEST_URI"] = r.RequestURI
	if r.RequestURI == "" {
		params["REQUEST_URI"] = r.URL.Path
	}
	params["DOCUMENT_URI"] = r.URL.Path

	// Server protocol and software
	params["SERVER_PROTOCOL"] = r.Proto
	params["SERVER_SOFTWARE"] = "Go-FastCGI-Server"

	// Remote address
	remoteAddr, remotePort, err := net.SplitHostPort(r.RemoteAddr)
	if err == nil {
		params["REMOTE_ADDR"] = remoteAddr
		params["REMOTE_PORT"] = remotePort
	}

	// Server name and port
	serverAddr, serverPort, err := net.SplitHostPort(r.Host)
	if err != nil {
		serverAddr = r.Host
		serverPort = "80"
		if r.TLS != nil {
			serverPort = "443"
		}
	}
	params["SERVER_NAME"] = serverAddr
	params["SERVER_PORT"] = serverPort

	// Query string
	params["QUERY_STRING"] = r.URL.RawQuery

	// Headers
	for header, values := range r.Header {
		header = strings.ToUpper(strings.Replace(header, "-", "_", -1))
		if header == "CONTENT_TYPE" {
			params["CONTENT_TYPE"] = values[0]
		} else if header == "CONTENT_LENGTH" {
			params["CONTENT_LENGTH"] = values[0]
		} else {
			params["HTTP_"+header] = values[0]
		}
	}

	// Content length
	if r.ContentLength > 0 {
		params["CONTENT_LENGTH"] = strconv.FormatInt(r.ContentLength, 10)
	}

	// Gateway interface
	params["GATEWAY_INTERFACE"] = "CGI/1.1"

	// Create FastCGI request
	fcgiReq := &Request{
		Params: params,
		Body:   body,
	}

	// Send request to FastCGI application
	response, err := client.Do(fcgiReq)
	if err != nil {
		http.Error(w, "Failed to process request", http.StatusBadGateway)
		slog.Error("FastCGI request error", "error", err)
		return
	}

	// Parse and send response
	s.parseAndSendResponse(w, response)
}

func (s *FastCGIServer) parseAndSendResponse(w http.ResponseWriter, response []byte) {
	// Split response into headers and body
	parts := strings.SplitN(string(response), "\r\n\r\n", 2)
	if len(parts) != 2 {
		http.Error(w, "Invalid response from FastCGI application", http.StatusBadGateway)
		return
	}

	// Parse headers
	headers := strings.Split(parts[0], "\r\n")
	for _, header := range headers {
		if header == "" {
			continue
		}
		headerParts := strings.SplitN(header, ":", 2)
		if len(headerParts) != 2 {
			continue
		}
		key := strings.TrimSpace(headerParts[0])
		value := strings.TrimSpace(headerParts[1])
		w.Header().Add(key, value)
	}

	// Write body
	fmt.Fprint(w, parts[1])
}

func main() {
	// Enable debug logging
	// slog.SetDefault(slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelDebug})))

	server := NewFastCGIServer(
		"child:9000", // FastCGI application address
	)

	// Create HTTP server
	http.Handle("/", server)

	slog.Info("Starting server on :9090")
	if err := http.ListenAndServe(":9090", nil); err != nil {
		slog.Error("Failed to start server", "error", err)
	}
}
