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

    let gov_path = Path::new("dataset/govdomains_latest.txt");
    let gov_contents_result = common::read_file_lines(gov_path);
    let gov_contents = match gov_contents_result {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}", error),
    };

    let url = "google.com";
    let res = ssl::get_issuer_for(url);
    println!(
        "issuer for {} is: {:?}",
        url,
        res.unwrap_or(format!("Error unwrapping issuer for url: {url}"))
    );

    while running.load(Ordering::SeqCst) {
        thread::sleep(Duration::from_millis(100));
        break;
    }
}
