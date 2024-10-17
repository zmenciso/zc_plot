use csv;
use std::fs::File;
use std::error::Error;
use regex::Regex;
use csv::Writer;

use crate::options::Options;

#[derive(Debug)]
pub struct DataFrame {
    pub header: Vec<String>,
    pub dims: Vec<Vec<f32>>
}

impl DataFrame {
    fn new() -> DataFrame {
        DataFrame {
            header: Vec::new(),
            dims: Vec::new()
        }
    }
}

fn si_convert(ins: &str) -> Result<String, Box<dyn Error>> {
    let re = Regex::new(r"[0-9\.-]+([munpfaKMGTP])")?;
    let prefix = re.captures(ins);

    if prefix.is_some() {
        let prefix = String::from(&prefix.unwrap()[1]);
        let repl = match prefix.as_str() {
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

        Ok(ins.replace(prefix.as_str(), repl))

    } else {
        Ok(String::from(ins))
    }
}


fn read_csv(filename: std::path::PathBuf, head: bool) -> Result<csv::Reader<File>, Box<dyn Error>> {
    let file = File::open(filename)?;
    let rdr = csv::ReaderBuilder::new()
        .has_headers(head)
        .from_reader(file);

    Ok(rdr)
}


fn update_header(df: &mut DataFrame, param: &str) {
    let owned = param.to_string();
    // Check if parameter is in header
    if !df.header.contains(&owned) {
        df.header.push(owned);

        // Add new dimension
        let u: Vec<f32> = Default::default();
        df.dims.push(u);
    }
}

fn push_val(df: &mut DataFrame, val: &str, addr: usize) {
    let value = si_convert(val).unwrap();

    let f = match value.parse::<f32>() {
        Ok(val) => val,
        Err(error) => {
            eprintln!("Could not decode value ({})", error);
            0.0
        },
    };

    df.dims[addr].push(f);
}

pub fn wave(filename: std::path::PathBuf, options: &mut Options) -> Result<DataFrame, Box<dyn Error>> {
    let mut rdr = read_csv(filename, true)?;
    let mut df = DataFrame::new();

    let headers = rdr.headers()?.clone();
    let headers: Vec<String> = headers.iter().map(String::from).collect();

    let (name, _g) = headers[0].split_once(' ').unwrap();
    options.update("x", "x");
    options.update("y", name);

    let mut setting: Vec<Vec<&str>> = Vec::new();

    update_header(&mut df, "x");
    update_header(&mut df, name);

    // Extract parameters
    for label in headers.iter() {
        if label.ends_with('Y') { continue; }

        let mut temp: Vec<&str> = Vec::new();
        let parameters: Vec<&str> = label.split(&['(', ')'][..]).collect();

        for param in (parameters[1]).split(',') {
            let (header, val) = param.split_once('=').unwrap();
            update_header(&mut df, header); 
            temp.push(val);
        }

        setting.push(temp);
    }

    // Add wave data
    for result in rdr.records() {
        let record = result?;

        for col in 0..record.len() {
            // x-axis
            if col % 2 == 0 {
                push_val(&mut df, &record[col], 0);
            }

            // y-axis
            if col % 2 == 1 {
                push_val(&mut df, &record[col], 1);

                // Push paramters
                for (i, dim) in setting[col/2].iter().enumerate() {
                    push_val(&mut df, dim, i+2);
                }
            }
        }
    }

    Ok(df)
}

pub fn summary(filename: std::path::PathBuf, options: &mut Options) -> Result<DataFrame, Box<dyn Error>> {
    let mut rdr = read_csv(filename, true)?;
    let mut df = DataFrame::new();
    let mut i = 0;

    for result in rdr.records() {
        let record = result?;

        // "Parameters" line
        if (&record[0]).contains("Parameters") {
            i = 0;
            let parameters: Vec<&str> = (&record[0]).strip_prefix("Parameters: ").unwrap().split(", ").collect();

            for param in parameters.iter() {
                let (header, val) = param.split_once('=').unwrap();

                update_header(&mut df, header);
                push_val(&mut df, val, i);
                i += 1;
            }
        }

        // Value line
        else if !(&record[3]).is_empty() {
            update_header(&mut df, &record[2]);
            push_val(&mut df, &record[3], i);
            i += 1;
        }
    }

    options.update("x", df.header[0].as_str());
    options.update("y", df.header[1].as_str());

    Ok(df)
}

pub fn raw(filename: std::path::PathBuf, options: &mut Options) -> Result<DataFrame, Box<dyn Error>> {
    let mut rdr = read_csv(filename, true)?;
    let mut df = DataFrame::new();

    let headers = rdr.headers()?.clone();
    df.header = headers.iter().map(String::from).collect();

    // TODO: There has to be a better way of doing this
    for _i in 0..df.header.len() {
        let v: Vec<f32> = Default::default();
        df.dims.push(v);
    }

    for result in rdr.records() {
        let record = result?;
        for i in 0..record.len() {
            push_val(&mut df, &record[i], i);
        }
    }

    options.update("x", df.header[0].as_str());
    options.update("y", df.header[1].as_str());

    Ok(df)
}

pub fn export(filename: std::path::PathBuf, df: DataFrame) -> Result<(), Box<dyn Error>> {
    let mut wtr = Writer::from_path(filename)?;

    wtr.write_record(&df.header)?;
    for row in 0..df.dims[0].len() {
        let mut vec: Vec<String> = Vec::new();
        for col in 0..df.dims.len() {
            vec.push(df.dims[col][row].to_string());
        }

        wtr.write_record(&vec)?;
    }

    Ok(())
}
