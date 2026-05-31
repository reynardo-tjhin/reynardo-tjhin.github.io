---
title: SSL/TLS Handshake
slug: ssl-tls-handshake
date: 2026-05-30
categories:
  - Web
description: Understanding SSL/TLS Handshake
comments: true
---

# Understanding SSL/TLS Handshake

I explain how SSL/TLS handshake works in an easy-to-understand manner in this blog post. I went a bit deeper on this topic because I thought one of the git problems that I faced was related to SSL/TLS handshake (You can read that here - [Issue: SSL certificate problem: unable to get local issuer certificate](/blog/2026/05/18/git-problems/#Issue:-SSL-certificate-problem:-unable-to-get-local-issuer%20certificate.)).

<!-- more -->

## Sources

I mainly learned how it works from these links:

- [How does SSL work?](https://www.cloudflare.com/learning/ssl/how-does-ssl-work/)
- [What Happens in a TLS Handshake?](https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/)

I find it easier if I can lay the details down in a simplified format.

## SSL/TLS Handshake

Below is the flow of TLS handshake using the RSA key exchange algorithm. However, the TLS handshake using the RSA key exchange algorithm is now considered not secure. The TLS handshake that uses RSA key exchange algorithm or other cipher suites that are vulnerable to attacks is now being replaced by TLS 1.3. Before going to TLS 1.3, I will explain the SSL/TLS handshake first.

There are two entities that are involved in a TLS handshake.

- `client`: the user that visits a domain
- `server`: the entity that handles/serves the client

A TLS handshake is necessary before any communication happens between the client and server to ensure that both parties are genuine. Clients do not want to talk to a server that can harm them. The communication is similar to how two people text.

### Part I: Ensuring Server is Genuine

In the first part of the communication, the client will try to verify that the server is genuine and safe before continuing with the rest of the communications. The client will request for SSL certificates that are compared against the Certificate Authority (CA). CA will check with its database and return whether the server is genuine.

```txt
client: "hello"
client: "here is a list of TLS version I support"
client: "here is a list of cipher suites I support"
client: "here is the random bytes I generate (also
         known as the 'client random')"

server: "hello"
server: "here is my SSL certificate. you can extract
         my public key inside"
server: "let's use this TLS version 'x.x'"
server: "let's use this 'xxx' cipher suite"
server: "here is the random bytes I generate (also
         known as the 'server random')"

client: "I have received your SSL certificate. I
         will now verify it with the certificate
         authority (CA) that issued your certificate."

client: ...opens local trust store...
client: ...uses CA's public key to verify the certificate's
           signature locally...

client: "I have verified and concluded you are not
         fake. We can continue our communication."
```

### Part II: Generate Session Keys

Once the client knows that the server is genuine, both the server and the client will generate the exact same session keys to communicate over the network. The communication will be encrypted with the session keys to ensure privacy.

```txt
client: ...generate another random string of bytes (
           also known as 'premaster secret')...
client: ...encrypt the 'premaster secret' with server's
           public key...

client: "Here is the premaster secret"
client: "I have encrypted it (the premaster secret) with
         your public key"

server: "I have received your premaster secret. I will
         now decrypt it using my private key"
server: "Now I'll generate session keys using your 'client
         random', your 'premaster secret' and my 'server
         random'"

client: "I have also generated session keys using my
         'client random', your 'server random' and my 
         'premaster secret'"
client: "I will encrypt my message 'finished' with the
         session keys"
client: "Here is my encrypted 'finished' message"

server: "I will decrypt your 'finished' message with my
         session keys"
server: "It says 'finished'. Our session keys match!"
server: "I will now encrypt my message 'finished'
         with our session keys"
server: "Here is my encrypted 'finished' message"

client: "I decrypted your 'finished' successfully!"
client: "We're synchronized and secure!"
```

The "finished" messages are the proof of matching keys, not a transmission of the keys themselves.

## Vulnerability with SSL/TLS Handshake

One of the ways to attack is via the Poodle Attack SSL which was discovered by Google security researches Bodo Möller, Thai Duong, and Krzysztof Kotowicz. Learn more about POODLE attack here - [What is Poodle Attack SSL](https://www.ssldragon.com/blog/what-is-poodle-attack-ssl/). The below shows how the attacker forces the client and the server to communicate using an unsafe SSL protocol.

```txt
client: "hello, I support TLS 1.2, 1.1, 1.0, SSL 3.0"

attacker: ...deliberately DISRUPTS/DROPS the handshake packets...
          ...causes a connection failure...

client: "let me retry with a lower version..."
client: "hello, I support TLS 1.1, 1.0, SSL 3.0"

attacker: ...disrupts again...

client: "let me retry again..."
client: "hello, I support TLS 1.0, SSL 3.0"

attacker: ...disrupts again...

client: "last resort..."
client: "hello, I support SSL 3.0 only"

server: "okay, SSL 3.0 it is!"

attacker: "perfect, now I can exploit CBC padding!"
```

Now both the server and the client are connected with SSL 3.0 that the attacker can attack easily. I'm not going to explain how SSL 3.0 can be attacked. It is above my pay grade. Essentially, the attacker will modify the encrypted message of the client. The server will respond with 'valid padding' or 'invalid padding'. The attacker will **mathematically determine** the plaintext data one byte at a time based on the server's response and the modified ciphertext. The response by the server is the 'oracle'. Hence, the name of this attack is called POODLE (Padding Oracle On Downgraded Legacy Encryption). The attacker does not need to know the session keys.

## Solution: Handshake in TLS 1.3

The simplified version (also as explained in [What Happens in a TLS Handshake?](https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/)) of the handshake in TLS 1.3 is as below.

Client sends 'hello' message with

- the protocol version
- the client random
- a list of cipher suites. 
- premaster secret parameters (the ingredients to calculate the premaster secret)

The client assumes that it knows the server's preferred key exchange method due to the limited number of cipher suites in TLS 1.3. This also speeds up the handshake in TLS 1.3.

After receiving the 'hello' message from the client, the server generates the master secret from

- the client random
- the client's premaster secret parameters
- the cipher suite chosen
- the server random

The server then sends the 'hello' message which includes

- the server's certificate
- the digital signature
- the server random
- the chosen cipher suite

Since the server already has the master secret, it also sends the 'finished' message.

The client then verifies signature and certificate. It also generates the master secret and sends its 'finished' message to the server.

TLS 1.3 includes performance improvements like 0-RTT (Zero Round-Trip Time), which reduces round trips for returning users. TLS 1.3 prevents the POODLE Attack SSL by completely rejecting SSL 3.0 and removing vulnerable CBC cipher suites entirely.

## Afterword

I didn't expect myself to go slightly deeper into the SSL/TLS handshake territory. After reading the blog posts from Cloudflare and back-and-forth questions with Claude, I finally gain a tiny bit understanding of the handshake that ensures the security and privacy of the communication between the client and the server.
