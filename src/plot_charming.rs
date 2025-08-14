use std::error::Error;
use charming::{Chart, component, ImageRenderer, series}

use crate::ingest::DataFrame;
use crate::options::Options;

pub fn plot(df: DataFrame, options: &Options) -> Result<(), Box<dyn Error>> {
    let mut chart: Chart = match options.retrieve("axes") {
        _ => {
            Chart::new()
                .grid(component::Grid::new())
                .x_axis(component::Axis::new())
                .y_axis(component::Axis::new())
        }
    };

    match options.retrieve("series") {
        "line" => { line(df, options, &mut chart); },
        "hist" => { hist(df, options, &mut chart); },
        _ => { line(df, &options, &mut chart); },
    }

    Ok(())
}

fn get_size(options: &Options) -> (u32, u32) {
    // TODO: Error handling
    let (xdim, ydim) = options.retrieve("figsize").split_once(',').unwrap();
    (xdim.parse::<u32>().unwrap(), ydim.parse::<u32>().unwrap())
}

fn line(df: DataFrame, options: &Options, chart: &mut Chart) {
    let (xdim, ydim) = get_size(&options);

    // TODO: Catch errors here
    let mut renderer = ImageRenderer::new(xdim, ydim);
    let filename = format!("{}.{}", 
        options.retrieve("filename"), 
        options.retrieve("filetype"));
    renderer.save(&chart, filename).unwrap();
   
    let line = series::Line::new();
    chart.series(line);
}    

fn hist(df: DataFrame, options: &Options, chart: &mut Chart) {
}
