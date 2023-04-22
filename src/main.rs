use num_cpus;
use std::path::Path;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use threadpool::ThreadPool;

mod common;
mod consts;
mod ssl;

fn main() {
    // TODO: Read THREAD_MULTIPLIER from args
    const THREAD_MULTIPLIER: usize = 2;
    let cpu_count = num_cpus::get();

    let gov_path = Path::new("dataset/government_domains_latest.txt");
    let gov_contents_result = common::read_file_lines(gov_path);
    let gov_contents = match gov_contents_result {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}", error),
    };

    let pool = ThreadPool::new(cpu_count * THREAD_MULTIPLIER);

    for url in gov_contents.iter() {
        let url_clone = url.to_string();
        let should_stop = Arc::new(AtomicBool::new(false));
        let should_stop_clone = should_stop.clone();
        pool.execute(move || {
            let info_result = ssl::get_issuer_for(&url_clone);
            let res = match info_result {
                Ok(info) => info,
                Err(error) => {
                    should_stop_clone.store(true, Ordering::Relaxed);
                    format!("Error getting the issuer for {}, err: {}", url_clone, error)
                }
            };

            let url_stats: Vec<String> = res.split(';').map(String::from).collect();
            if should_stop_clone.load(Ordering::Relaxed) {
                return;
            }
            if res.len() == 1 {
                should_stop_clone.store(true, Ordering::Relaxed);
                return;
            }
            if url_stats[1].contains("Russian Trusted") {
                println!("\x1b[93m{} – {}\x1b[0m", url_clone, url_stats[1])
            } else {
                println!("{} skipped", url_clone)
            }
            should_stop_clone.store(true, Ordering::Relaxed);
        });

        let should_stop_clone = should_stop.clone();
        let _ = thread::spawn(move || {
            thread::sleep(std::time::Duration::from_secs(1));
            should_stop_clone.store(true, Ordering::Relaxed);
        });

        while !should_stop.load(Ordering::Relaxed) {
            thread::yield_now();
        }
    }

    pool.join();
}
