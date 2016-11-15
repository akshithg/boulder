package creds

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"math/big"
	"net"
	"net/http/httptest"
	"testing"
	"time"

	"golang.org/x/net/context"

	"github.com/letsencrypt/boulder/core"
	"github.com/letsencrypt/boulder/test"
)

func TestServerTransportCredentials(t *testing.T) {
	acceptedSANs := map[string]struct{}{
		"boulder-client": struct{}{},
	}
	goodCert, err := core.LoadCert("../../test/grpc-creds/boulder-client/cert.pem")
	test.AssertNotError(t, err, "core.LoadCert('../../grpc-creds/boulder-client/cert.pem') failed")
	badCert, err := core.LoadCert("../../test/test-root.pem")
	test.AssertNotError(t, err, "core.LoadCert('../../test-root.pem') failed")
	servTLSConfig := &tls.Config{}

	// NewServerCredentials with a nil serverTLSConfig should return an error
	_, err = NewServerCredentials(nil, acceptedSANs)
	test.AssertEquals(t, err, NilServerConfigErr)

	// A creds with a nil acceptedSANs list should consider any peer valid
	bcreds := &serverTransportCredentials{servTLSConfig, nil}
	emptyState := tls.ConnectionState{}
	err = bcreds.validateClient(emptyState)
	test.AssertNotError(t, err, "validateClient() errored for emptyState")

	// A creds given an empty TLS ConnectionState to verify should return an error
	bcreds = &serverTransportCredentials{servTLSConfig, acceptedSANs}
	err = bcreds.validateClient(emptyState)
	test.AssertEquals(t, err, EmptyPeerCertsErr)

	// A creds should reject peers that don't have a leaf certificate with
	// a SAN on the accepted list.
	wrongState := tls.ConnectionState{
		PeerCertificates: []*x509.Certificate{badCert},
	}
	err = bcreds.validateClient(wrongState)
	test.AssertEquals(t, err, SANNotAcceptedErr)

	// A creds should accept peers that have a leaf certificate with a SAN
	// that is on the accepted list
	rightState := tls.ConnectionState{
		PeerCertificates: []*x509.Certificate{goodCert},
	}
	err = bcreds.validateClient(rightState)
	test.AssertNotError(t, err, "validateClient(rightState) failed")

	// A creds configured with an IP SAN in the accepted list should accept a peer
	// that has a leaf certificate containing an IP address SAN present in the
	// accepted list.
	acceptedIPSans := map[string]struct{}{
		"127.0.0.1": struct{}{},
	}
	bcreds = &serverTransportCredentials{servTLSConfig, acceptedIPSans}
	err = bcreds.validateClient(rightState)
	test.AssertNotError(t, err, "validateClient(rightState) failed with an IP accepted SAN list")
}

func TestClientTransportCredentials(t *testing.T) {
	priv, err := rsa.GenerateKey(rand.Reader, 1024)
	test.AssertNotError(t, err, "rsa.GenerateKey failed")

	temp := &x509.Certificate{
		SerialNumber: big.NewInt(1),
		Subject: pkix.Name{
			CommonName: "A",
		},
		NotBefore:             time.Unix(1000, 0),
		NotAfter:              time.Now().AddDate(1, 0, 0),
		BasicConstraintsValid: true,
		IsCA: true,
	}
	derA, err := x509.CreateCertificate(rand.Reader, temp, temp, priv.Public(), priv)
	test.AssertNotError(t, err, "x509.CreateCertificate failed")
	certA, err := x509.ParseCertificate(derA)
	test.AssertNotError(t, err, "x509.ParserCertificate failed")
	temp.Subject.CommonName = "B"
	derB, err := x509.CreateCertificate(rand.Reader, temp, temp, priv.Public(), priv)
	test.AssertNotError(t, err, "x509.CreateCertificate failed")
	certB, err := x509.ParseCertificate(derB)
	test.AssertNotError(t, err, "x509.ParserCertificate failed")
	roots := x509.NewCertPool()
	roots.AddCert(certA)
	roots.AddCert(certB)

	serverA := httptest.NewUnstartedServer(nil)
	serverA.TLS = &tls.Config{Certificates: []tls.Certificate{{Certificate: [][]byte{derA}, PrivateKey: priv}}}
	serverB := httptest.NewUnstartedServer(nil)
	serverB.TLS = &tls.Config{Certificates: []tls.Certificate{{Certificate: [][]byte{derB}, PrivateKey: priv}}}

	tc := NewClientCredentials(roots, []tls.Certificate{})

	serverA.StartTLS()
	defer serverA.Close()
	addrA := serverA.Listener.Addr().String()
	rawConnA, err := net.Dial("tcp", addrA)
	test.AssertNotError(t, err, "net.Dial failed")
	defer func() {
		_ = rawConnA.Close()
	}()

	conn, _, err := tc.ClientHandshake(context.Background(), "A:2020", rawConnA)
	test.AssertNotError(t, err, "tc.ClientHandshake failed")
	test.Assert(t, conn != nil, "tc.ClientHandshake returned a nil net.Conn")

	serverB.StartTLS()
	defer serverB.Close()
	addrB := serverB.Listener.Addr().String()
	rawConnB, err := net.Dial("tcp", addrB)
	test.AssertNotError(t, err, "net.Dial failed")
	defer func() {
		_ = rawConnB.Close()
	}()

	conn, _, err = tc.ClientHandshake(context.Background(), "B:3030", rawConnB)
	test.AssertNotError(t, err, "tc.ClientHandshake failed")
	test.Assert(t, conn != nil, "tc.ClientHandshake returned a nil net.Conn")

	// Test timeout
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	test.AssertNotError(t, err, "net.Listen failed")
	defer func() {
		_ = ln.Close()
	}()
	addrC := ln.Addr().String()
	stop := make(chan struct{}, 1)
	go func() {
		for {
			select {
			case <-stop:
				return
			default:
				_, _ = ln.Accept()
				time.Sleep(2 * time.Millisecond)
			}
		}
	}()

	rawConnC, err := net.Dial("tcp", addrC)
	test.AssertNotError(t, err, "net.Dial failed")
	defer func() {
		_ = rawConnB.Close()
	}()

	ctx, cancel := context.WithTimeout(context.Background(), time.Millisecond)
	defer cancel()
	conn, _, err = tc.ClientHandshake(ctx, "A:2020", rawConnC)
	test.AssertError(t, err, "tc.ClientHandshake didn't timeout")
	test.AssertEquals(t, err.Error(), "boulder/grpc/creds: context deadline exceeded")
	test.Assert(t, conn == nil, "tc.ClientHandshake returned a non-nil net.Conn on failure")

	stop <- struct{}{}
}
