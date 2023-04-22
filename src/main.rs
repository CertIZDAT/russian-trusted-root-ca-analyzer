use num_threads;
use std::num::NonZeroUsize;
use std::path::Path;
use std::str::FromStr;
use threadpool::ThreadPool;

mod common;
mod consts;
mod ssl;

fn main() {
    let cpu_count = num_threads::num_threads();

    let gov_path = Path::new("dataset/government_domains_latest.txt");
    let gov_contents_result = common::read_file_lines(gov_path);
    let gov_contents = match gov_contents_result {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}", error),
    };

    let pool =
        ThreadPool::new(4 * usize::from(cpu_count.unwrap_or(NonZeroUsize::from_str("1").unwrap())));

    for url in gov_contents.iter() {
        let url_clone = url.to_string();
        pool.execute(move || {
            let info_result = ssl::get_issuer_for(&url_clone);
            let res = match info_result {
                Ok(info) => info,
                Err(error) => {
                    format!("Error getting the issuer for {}, err: {}", url_clone, error);
                    return;
                }
            };
            let url_stats: Vec<String> = res.split(';').map(String::from).collect();
            if url_stats[1].contains("Russian Trusted") {
                println!("{} – {}", url_clone, url_stats[1])
            } else {
                println!("{} skipped", url_clone)
            }
        });
    }

    pool.join()
}
