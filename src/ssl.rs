use openssl::ssl::{SslConnector, SslMethod};
use std::error::Error;
use std::net::{SocketAddr, TcpStream, ToSocketAddrs};
use std::result::Result;
use std::time::Duration;
use std::time::Instant;

// const HEADER: &[(&str, &str)] = &[("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")];

pub(crate) fn get_issuer_for(url: &str) -> Result<String, Box<dyn Error>> {
    // let headers = HEADER.iter().map(|(k, v)| (*k, *v)).collect::<HashMap<_, _>>();

    let connector = SslConnector::builder(SslMethod::tls()).unwrap().build();
    let host = format!("{}:{}", url, 443);
    let mut addrs = host.to_socket_addrs().unwrap();

    // Get the first address from the vector
    let socket_data = addrs.next().unwrap();
    let socket_addr = SocketAddr::new(socket_data.ip(), socket_data.port());

    let timeout = Duration::from_secs(5);
    let start = Instant::now(); // Start timer
    match TcpStream::connect_timeout(&socket_addr, timeout) {
        Ok(stream) => {
            match connector.connect(&url, stream) {
                Ok(ssl_stream) => {
                    let cert = ssl_stream.ssl().peer_certificate().unwrap();

                    // Extract the SSL issuer from the certificate
                    let issuer = cert
                        .issuer_name()
                        .entries()
                        .find(|entry| entry.object().nid() == openssl::nid::Nid::COMMONNAME)
                        .unwrap()
                        .data()
                        .as_utf8()
                        .unwrap()
                        .to_string();

                    let duration = start.elapsed(); // Stop timer
                    if duration.as_secs() >= 5 {
                        return Err(format!("Timeout error").into());
                    }

                    Ok(issuer)
                }
                Err(err) => {
                    return Err(Box::new(err));
                }
            }
        }
        Err(e) => {
            eprintln!("Error connecting to {}: {:?}", url, e);
            Err(format!("Error connecting to {url}: {e}").into())
        }
    }
}
