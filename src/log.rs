use std::error::Error;
use std::fs::File;

use crate::options::Options;

pub fn log(filename: std::path::PathBuf, options: Options, input: std::path::PathBuf, config: std::path::PathBuf) -> Result<(), Box<dyn Error>> {
    let (day, time) = options.retrieve("time").unwrap().split_once('T').unwrap();
    let content = format!("ZC Plot \
        Executed on {} at {} \
        \
        Data file: {:?}\
        Options file: {:?}\
        ",
        day,
        time,
        input,
        config);

    // let mut file = File::create(filename)?;
    // file.write_all(content.as_bytes())?;
    // file.write_all(options.pprint().as_bytes())?;

    Ok(())
}
