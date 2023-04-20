use std::path::Path;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

mod common;
mod consts;
mod ssl;

fn main() {
    let running: Arc<AtomicBool> = Arc::new(AtomicBool::new(true));
    let r: Arc<AtomicBool> = running.clone();

    // Set control-c handler
    ctrlc::set_handler(move || {
        r.store(false, Ordering::SeqCst);
    })
    .expect("Error setting Ctrl-C handler");

    let gov_path = Path::new("dataset/government_domains_latest.txt");
    let gov_contents_result = common::read_file_lines(gov_path);
    let gov_contents = match gov_contents_result {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}", error),
    };

    for url in gov_contents.iter() {
        println!("url: {:?}", url);
        let _ = ssl::get_issuer_for(url);

        // if let Ok(issuer) = ssl::get_issuer_for(url)) {
        //     let url_issuer = format!("{}: {}", url, issuer);
        //     println!("{}", url_issuer);
        // } else {
        //     println!("Failed to get SSL issuer for {}", url);
        // }
    }

    while running.load(Ordering::SeqCst) {
        thread::sleep(Duration::from_millis(100));
        break;
    }
}
