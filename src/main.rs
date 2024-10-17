use clap::Parser;
use std::error::Error;

pub mod ingest;
pub mod options;
pub mod plot;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    config: std::path::PathBuf,
    path: std::path::PathBuf,

    #[arg(short, long, default_value = "wave")]
    dtype: Option<String>,

    #[arg(short, long)]
    export: Option<std::path::PathBuf>,

    #[arg(short, long)]
    interact: bool,
    #[arg(short, long)]
    quiet: bool,
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse();
    let df: ingest::DataFrame;

    let mut options = options::read(args.config)?;

    match args.dtype.unwrap().as_str() {
        "wave" => { df = ingest::wave(args.path, &mut options)?; },
        "summary" => { df = ingest::summary(args.path, &mut options)?; },
        "raw" => { df = ingest::raw(args.path, &mut options)?; },
        _ => { df = ingest::raw(args.path, &mut options)?; },
    }

    if args.export.is_some() {
        ingest::export(args.export.unwrap(), df)?;
    }

    Ok(())
}
