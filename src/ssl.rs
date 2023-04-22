use openssl::ssl::{SslConnector, SslMethod};
use std::error::Error;
use std::net::{SocketAddr, TcpStream, ToSocketAddrs};
use std::result::Result;
use std::time::Duration;

// TODO: implement custom header usage
// const HEADER: &[(&str, &str)] = &[("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")];

pub(crate) fn get_issuer_for(url: &str) -> Result<String, Box<dyn Error>> {
    const SSL_TIMEOUT: Duration = Duration::from_secs(5);

    // Set up a SSL connector with custom options
    let mut ssl_connector_builder = SslConnector::builder(SslMethod::tls()).unwrap();
    let host = format!("{}:{}", url, 443);
    let mut socket_addr = match host.to_socket_addrs() {
        Ok(addrs) => addrs,
        Err(error) => {
            return Err(format!("Socket Address unwrap error: {}", error).into());
        }
    };

    // Get the first address from the vector
    let socket_data = socket_addr.next().unwrap();
    let socket_addr = SocketAddr::new(socket_data.ip(), socket_data.port());
    ssl_connector_builder
        .set_verify_callback(openssl::ssl::SslVerifyMode::NONE, |_preverify_ok, _cert| {
            true
        });

    // Connect to the remote host and negotiate the SSL handshake
    let stream = TcpStream::connect_timeout(&socket_addr, SSL_TIMEOUT)?;
    let ssl_stream = ssl_connector_builder
        .build()
        .connect(url, stream)
        .map_err(|e| (e))?;

    // Get the peer certificate and extract the issuer name
    let cert = ssl_stream.ssl().peer_certificate().unwrap();
    let issuer_name: Vec<String> = cert
        .issuer_name()
        .entries()
        .map(|entry| entry.data().as_utf8().unwrap().to_string())
        .collect();

    Ok(format!("{};{}", url, issuer_name[2]).to_string())
}
