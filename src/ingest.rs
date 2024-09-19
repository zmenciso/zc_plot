use csv;
use std::fs::File;
use std::error::Error;
use regex::Regex;

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
    let re = Regex::new(r"[0-9\.-]+([a-zA-Z])")?;
    let prefix = re.captures(ins);

    if prefix.is_some() {
        let prefix = String::from(&prefix.unwrap()[1]);
        let repl = match prefix.as_str() {
            "m" => "1e-3",
            "u" => "1e-6",
            "n" => "1e-9",
            "p" => "1e-12",
            "f" => "1e-15",
            "a" => "1e-18",
            "K" => "1e3",
            "M" => "1e6",
            "G" => "1e9",
            "T" => "1e12",
            "P" => "1e15",
            _ => "1e1"
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

fn update_header(df: &mut DataFrame, param: String) {
    // Check if parameter is in header
    if !df.header.contains(&param) {
        df.header.push(param);

        // Add new dimension
        // TODO: There has to be a better way of doing this
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

pub fn wave(filename: std::path::PathBuf) -> Result<DataFrame, Box<dyn Error>> {
    let mut rdr = read_csv(filename, true)?;
    let mut df = DataFrame::new();

    let headers = rdr.headers()?.clone();
    let headers: Vec<String> = headers.iter().map(String::from).collect();




    for result in rdr.records() {
    }

    Ok(df)
}

pub fn summary(filename: std::path::PathBuf) -> Result<DataFrame, Box<dyn Error>> {
    let mut rdr = read_csv(filename, true)?;
    let mut df = DataFrame::new();
    let mut i = 0;

    for result in rdr.records() {
        let record = result?;

        // "Parameters" line
        if (&record[0]).contains("Parameters") {
            i = 0;
            let parameters: Vec<&str> = (&record[0]).strip_prefix("Parameters: ").unwrap().split(", ").collect();
            println!("{:?}", parameters);

            for param in parameters.iter() {
                let (header, val) = param.split_once('=').unwrap();

                update_header(&mut df, String::from(header));
                push_val(&mut df, val, i);
                i += 1;
            }
        }

        // Value line
        else if !(&record[3]).is_empty() {
            update_header(&mut df, String::from(&record[2]));
            push_val(&mut df, &record[3], i);
            i += 1;
        }
    }

    Ok(df)
}

pub fn raw(filename: std::path::PathBuf) -> Result<DataFrame, Box<dyn Error>> {
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

    Ok(df)
}
