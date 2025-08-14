use charming::{
    Chart,
};
use std::error::Error;

use crate::ingest::DataFrame;
use crate::options::Options;

pub fn plot(df: &DataFrame, options: &Options) -> Result<(), Box<dyn Error>> {
    let mut chart = match options.retrieve("series") {
        Some("line") => { line(df, options, &mut chart); },
        Some("hist") => { hist(df, options, &mut chart); },
        None => { line(df, &options, &mut chart); },
    };

    Ok(())
}

fn line (df: &DataFrame, options: &Options, &mut chart: Plot2D) -> Chart {

}
