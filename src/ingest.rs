use csv;
use std::fs::File;
use std::error::Error;
use regex::Regex;
use csv::Writer;
use std::collections::HashMap;

use crate::options::Options;


pub type DataFrame = Vec<Series>;

#[derive(Debug)]
pub struct DataPoint {
    pub x: f32,
    pub y: f32,
}

#[derive(Debug)]
pub struct Series {
    pub name: String,
    pub parameters: HashMap<String, f32>,
    pub data: Vec<DataPoint>,
}

impl Series {
    pub fn new(name: &str) -> Series {
        Series {
            name: name.to_string(),
            parameters: HashMap::new(),
            data: Vec::new()
        }
    }

    pub fn add_param(&mut self, param: &str, val: &str) {
        self.parameters.insert(
            param.to_string(),
            Self::decode_str(val),
        );
    }

    fn decode_str(val: &str) -> f32 {
        match val.parse::<f32>() {
            Ok(val) => val,
            Err(error) => {
                eprintln!("Could not decode value ({})", error);
                0.0
            },
        }
    }

    fn decode_si(ins: &str) -> f32 {
        let re = Regex::new(r"[0-9\.-]+([munpfaKMGTP])").unwrap();
        let prefix = re.captures(ins);

        if prefix.is_some() {
            let prefix = &prefix.unwrap()[1];
            let repl = match prefix {
                "m" => "e-3",
                "u" => "e-6",
                "n" => "e-9",
                "p" => "e-12",
                "f" => "e-15",
                "a" => "e-18",
                "K" => "e3",
                "M" => "e6",
                "G" => "e9",
                "T" => "e12",
                "P" => "e15",
                _ => "e1"
            };

            Self::decode_str(ins.replace(prefix, repl).as_str())

        } else {
            Self::decode_si(ins)
        }
    }

    pub fn push_str(&mut self, x: &str, y: &str) {
        let d = DataPoint {
            x: Self::decode_str(x),
            y: Self::decode_str(y),
        };

        self.data.push(d);
    }

    pub fn push_si(&mut self, x: &str, y: &str) {
        let d = DataPoint {
            x: Self::decode_si(x),
            y: Self::decode_si(y),
        };

        self.data.push(d);
    }
}

fn read_csv(filename: std::path::PathBuf, head: bool) -> Result<csv::Reader<File>, Box<dyn Error>> {
    let file = File::open(filename)?;
    let rdr = csv::ReaderBuilder::new()
        .has_headers(head)
        .from_reader(file);

    Ok(rdr)
}

pub fn wave(filename: std::path::PathBuf, options: &mut Options) -> Result<DataFrame, Box<dyn Error>> {
    let mut rdr = read_csv(filename, true)?;
    let mut df: DataFrame = Vec::new();

    let headers = rdr.headers()?.clone();

    // Create all series
    for (i, label) in headers.iter().enumerate() {
        if label.ends_with('Y') { continue; }

        // Create new series
        let (name, _g) = label.split_once(' ').unwrap();
        df.push(Series::new(name));

        let parameters: Vec<&str> = label.split(&['(', ')'][..]).collect();
        for param in parameters[1].split(',') {
            let (header, val) = param.split_once('=').unwrap();
            df[i/2].add_param(header, val);
        }
    }

    // Add wave data
    for result in rdr.records() {
        let record = result?;

        for col in (0..record.len()).step_by(2) {
            df[col/2].push_str(&record[col], &record[col+1]);
        }
    }

    options.update("y", &df[0].name);

    Ok(df)
}

/*
pub fn summary(filename: std::path::PathBuf, options: &mut Options) -> Result<DataFrame, Box<dyn Error>> {
    let mut rdr = read_csv(filename, true)?;
    let mut df: DataFrame = Vec::new();

    let pivot: Option<&str> = options.retrieve("x");
    let mut pivot = match pivot {
        Some(val) => String::from(val),
        None => String::from("")
    };

    let mut i = 0;
    let mut x: String;

    for result in rdr.records() {
        let record = result?;

        // "Paramters" line
        if (&record[0]).contains("Parameters") {
            let parameters = (&record[0]).strip_prefix("Parameters: ").unwrap().split(", ");

            for param in parameters {
                let (header, val) = param.split_once('=').unwrap();

                // If no pivot, take first param as pivot
                if pivot.is_empty() {
                    pivot = String::from(header);
                }

                // Store pivot param as x for series
                if header == pivot {
                    x = String::from(val);
                }
                // Remaining parameters become series parameters
                else {
                    df[i].add_param(header, val);
                }

            }
        }

        // Value line
        else if !(&record[3]).is_empty() {
        }

    }

    Ok(df)
}
*/

pub fn export(filename: std::path::PathBuf, df: DataFrame) -> Result<(), Box<dyn Error>> {
    let mut wtr = Writer::from_path(filename)?;
    let mut record: Vec<String> = Vec::new();

    // Compose header
    for series in df {
        let mut temp = format!("{} (", series.name);
        for (param, value) in series.parameters {
            temp = format!("{}{}={}, ", temp, param, value);
        }
        record.push(format!("{}) x", temp));
        record.push(format!("{}) y", temp));
    }

    wtr.write_record(record)?;

    // Compose records

    Ok(())
}
