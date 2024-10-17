use std::error::Error;
use charming::Chart;
use charming::component;
use charming::ImageRenderer;

use crate::ingest::DataFrame;
use crate::options::Options;

pub fn plot(df: DataFrame, options: Options) -> Result<(), Box<dyn Error>> {
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
        _ => { line(df, options, &mut chart); },
    }

    Ok(())
}

fn line(df: DataFrame, options: Options, chart: &mut Chart) {

    // TODO: Catch errors here
    let mut renderer = ImageRenderer::new(1000, 800);
    renderer.save(&chart, options.retrieve("filename")).unwrap();
}
