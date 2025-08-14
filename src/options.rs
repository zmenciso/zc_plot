use std::collections::HashMap;
use std::{fs,fmt};
use std::error::Error;
use std::io::{BufRead, BufReader};
use chrono::Local;

#[derive(Debug)]
pub struct Options {
    options: HashMap<String, String>
}

impl Options {
    fn new() -> Options {
        let dt = Local::now();
        let timestamp = dt.format("%Y-%m-%dT%H:%M:%s");

        Options {
            options: HashMap::from([
                ("series".to_string(), "line".to_string()),
                ("axes".to_string(), "rectangular".to_string()),
                ("time".to_string(), timestamp.to_string()),
                ("figsize".to_string(), "600,300".to_string()),
                ("filename".to_string(), timestamp.to_string()),
                ("filetype".to_string(), "svg".to_string()),
            ])
        }
    }

    pub fn update(&mut self, key: &str, value: &str) {
        self.options.insert(
            key.to_string().to_lowercase(),
            value.to_string().to_lowercase()
        );
    }

    pub fn retrieve(&self, key: &str) -> Option<&String> {
        self.options.get(key)
    }
}

impl fmt::Display for Options {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let mut output: String = "Options:\n".to_owned();
        for (opt, val) in &self.options {
            output = format!("    {}: {}", opt, val);
        }
        write!(f, "{}", output)
    }
}

pub fn read(filename: std::path::PathBuf) -> Result<Options, Box<dyn Error>> {
    let mut options = Options::new();

    let file = fs::File::open(filename)?;
    let rdr = BufReader::new(file);

    for line in rdr.lines() {
        let line = line.unwrap();
        if line.trim().starts_with('#') { continue; }

        if let Some((param, value)) = line.split_once(':') {
            options.update(
                param.trim(),
                value.trim()
            );
        } else {
            eprintln!("Delimeter not found in string.");
        }
    }

    Ok(options)
}
