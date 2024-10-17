use std::collections::HashMap;
use std::fs;
use std::error::Error;
use std::io::{BufRead, BufReader};

#[derive(Debug)]
pub struct Options {
    options: HashMap<String, String>
}

impl Options {
    fn new() -> Options {
        Options {
            options: HashMap::from([
                ("series".to_string(), "line".to_string()),
                ("axes".to_string(), "rectangular".to_string()),
            ])
        }
    }

    pub fn update(&mut self, key: String, value: String) {
        self.options.insert(
            key,
            value
        );
    }

    pub fn retrieve(&self, key: String) -> String {
        if self.options.contains_key(&key) {
            self.options.get(&key).unwrap().to_string()
        }
        else {
            "None".to_string()
        }
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
