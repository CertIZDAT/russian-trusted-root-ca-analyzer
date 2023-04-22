use std::path::Path;

mod common;
mod consts;
mod ssl;

fn main() {
    let gov_path = Path::new("dataset/government_domains_latest.txt");
    let gov_contents_result = common::read_file_lines(gov_path);
    let gov_contents = match gov_contents_result {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}", error),
    };

    for url in gov_contents.iter() {
        let info_result = ssl::get_issuer_for(url);
        let res = match info_result {
            Ok(info) => info,
            Err(error) => {
                format!("Error getting the issuer for {}, err: {}", url, error);
                continue;
            }
        };
        let url_stats: Vec<String> = res.split(';').map(String::from).collect();
        if url_stats[1].contains("Russian Trusted") {
            println!("{} – {}", url, url_stats[1])
        } else {
            println!("{} skipped", url)
        }
    }
}
