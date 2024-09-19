use clap::Parser;
use std::error::Error;

mod ingest;
mod options;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    config: std::path::PathBuf,
    path: std::path::PathBuf,

    #[arg(short, long, default_value = "wave")]
    dtype: Option<String>,

    #[arg(short, long)]
    interact: bool,
    #[arg(short, long)]
    quiet: bool,
    #[arg(short, long)]
    export: bool,
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse();
    let df: ingest::DataFrame;

    match args.dtype.unwrap().as_str() {
        "wave" => { df = ingest::wave(args.path)?; },
        "summary" => { df = ingest::summary(args.path)?; },
        "raw" => { df = ingest::raw(args.path)?; },
        _ => { df = ingest::raw(args.path)?; },
    }

    let ingest::DataFrame { header, dims } = df;
    println!("header: {:?}", header);
    println!("dims: {:?}", dims);

    let options = options::read(args.config)?;
    println!("{:?}", options);

    Ok(())
}
