use std::collections::HashMap;
use std::fs;
use std::error::Error;
use std::io::{BufRead, BufReader};

pub fn read(filename: std::path::PathBuf) -> Result<HashMap<String, String>, Box<dyn Error>> {
    let mut options = HashMap::new();

    let file = fs::File::open(filename)?;
    let rdr = BufReader::new(file);

    for line in rdr.lines() {
        let line = line.unwrap();
        if let Some((param, value)) = line.split_once(':') {
            options.insert(
                // TODO: There has to be a better way to do this
                param.trim().to_string(),
                value.trim().to_string(),
            );
        } else {
            eprintln!("Delimeter not found in string.");
        }
    }

    Ok(options)
}
