use text_io::read;
use std::collections::HashMap;

pub fn query(prompt: &str, default: Option<&str>) -> bool {
    // Wait for upser to input a y/n, with support for default
    let valid: HashMap<&str, bool> = HashMap::from([
        ("yes", true),
        ("y", true),
        ("ye", true),
        ("no", false),
        ("n", false)
    ]);

    let sel = match default {
        Some("yes") => "[Y/n]",
        Some("no") => "[y/N]",
        _ => "[y/n]",
    };

    loop {
        print!("\033[93m{}{}\x1b[0m", prompt, sel);
        let response: String = read!();
        if default.is_some() & (response.len() == 0) {
            return valid.get(default.unwrap()).unwrap().to_owned();
        }
        else if valid.contains_key(response.as_str()) {
            return valid.get(response.as_str()).unwrap().to_owned();
        }
    }
}
