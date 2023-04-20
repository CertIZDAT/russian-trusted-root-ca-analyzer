use openssl::ssl::{HandshakeError, SslConnector, SslMethod};
use std::error::Error;
use std::net::{SocketAddr, TcpStream, ToSocketAddrs};
use std::process::exit;
use std::result::Result;
use std::time::Duration;
use std::time::Instant;

// const HEADER: &[(&str, &str)] = &[("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")];

pub(crate) fn get_issuer_for(url: &str) -> Result<String, Box<dyn Error>> {
    let ssl_timeout = std::time::Duration::from_secs(5);

    // Set up a SSL connector with custom options
    let mut ssl_connector_builder = SslConnector::builder(SslMethod::tls()).unwrap();
    let host = format!("{}:{}", url, 443);
    let mut socket_addr = match host.to_socket_addrs() {
        Ok(addrs) => addrs,
        Err(error) => {
            return Err(format!("addrs unwrap error: {}", error).into());
        }
    };

    // Get the first address from the vector
    let socket_data = socket_addr.next().unwrap();
    let socket_addr = SocketAddr::new(socket_data.ip(), socket_data.port());
    ssl_connector_builder
        .set_verify_callback(openssl::ssl::SslVerifyMode::NONE, |_preverify_ok, _cert| {
            true
        });
    // println!("ssl connector builder");
    // Connect to the remote host and negotiate the SSL handshake
    let stream = TcpStream::connect_timeout(&socket_addr, ssl_timeout)?;
    // println!("stream: {:?}", stream);
    let ssl_stream = ssl_connector_builder
        .build()
        .connect(url, stream)
        .map_err(|e| (e))?;

    // Get the peer certificate and extract the issuer name
    let cert = ssl_stream.ssl().peer_certificate().unwrap();
    let i: Vec<String> = cert
        .issuer_name()
        .entries()
        .map(|entry| entry.data().as_utf8().unwrap().to_string())
        .collect();
    println!("cert {:?}", i[2]);
    let issuer_name = cert
        .issuer_name()
        .entries()
        .next()
        .unwrap()
        .data()
        .as_utf8()
        .unwrap();
    // println!("Issuer name: {}", issuer_name);
    Ok(issuer_name.to_string())

    //     return Ok("s".to_string());
    //     exit(0);
    //
    //     const FUNC_TIMEOUT_IN_SEC: u64 = 30;
    //     // let headers = HEADER.iter().map(|(k, v)| (*k, *v)).collect::<HashMap<_, _>>();
    //
    //     let connector = SslConnector::builder(SslMethod::tls()).unwrap().build();
    //     let host = format!("{}:{}", url, 443);
    //     let mut addrs = match host.to_socket_addrs() {
    //         Ok(addrs) => addrs,
    //         Err(error) => {
    //             return Err(format!("addrs unwrap error: {}", error).into());
    //         }
    //     };
    //
    //     // Get the first address from the vector
    //     let socket_data = addrs.next().unwrap();
    //     let socket_addr = SocketAddr::new(socket_data.ip(), socket_data.port());
    //
    //     let ssl_timeout = Duration::from_secs(FUNC_TIMEOUT_IN_SEC - 1);
    //     let start = Instant::now(); // Start timer
    //     match TcpStream::connect_timeout(&socket_addr, ssl_timeout) {
    //         Ok(stream) => {
    //             match connector.connect(&url, stream) {
    //                 Ok(ssl_stream) => {
    //                     println!("ssl_streamed");
    //                     let cert = ssl_stream.ssl().peer_certificate().unwrap();
    //                     // TODO: Strange timeout behavior: tula.vybory.izbirkom.ru etc...
    //                     // Extract the SSL issuer from the certificate
    //                     println!("cert: {:?}", cert);
    //                     let issuer = cert
    //                         .issuer_name()
    //                         .entries()
    //                         .find(|entry| entry.object().nid() == openssl::nid::Nid::COMMONNAME)
    //                         .unwrap()
    //                         .data()
    //                         .as_utf8()
    //                         .unwrap()
    //                         .to_string();
    //
    //                     let duration = start.elapsed(); // Stop timer
    //                     if duration.as_secs() >= FUNC_TIMEOUT_IN_SEC {
    //                         return Err(format!("Timeout error").into());
    //                     }
    //
    //                     Ok(issuer)
    //                 }
    //                 Err(err) => {
    //                     println!("!ssl_streamed");
    //                     return Err(Box::new(err));
    //                 }
    //             }
    //         }
    //         Err(e) => {
    //             eprintln!("Error connecting to {}: {:?}", url, e);
    //             Err(format!("Error connecting to {url}: {e}").into())
    //         }
    //     }
}
