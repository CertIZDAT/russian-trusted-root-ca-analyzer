use std::error::Error;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;

pub(crate) fn read_file_lines(path: &Path) -> Result<Vec<String>, Box<dyn Error>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let mut lines = Vec::new();
    for line in reader.lines() {
        let line = line?;

        // Skip empty lines and comment lines that start with '#'
        if line.trim().is_empty() || line.trim().starts_with('#') {
            continue;
        }

        let line = format!("https://{}", line.trim());
        lines.push(line);
    }

    Ok(lines)
}
