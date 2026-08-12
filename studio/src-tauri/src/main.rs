#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::env;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::{Manager, RunEvent};

struct ServiceChild(Mutex<Option<Child>>);

fn start_service() -> Option<Child> {
    let port = env::var("MEMCODER_STUDIO_PORT").unwrap_or_else(|_| "8765".to_string());
    let mut command = if let Ok(python) = env::var("MEMCODER_PYTHON") {
        let mut value = Command::new(python);
        value.args(["-m", "memcoder", "service", "serve"]);
        value
    } else {
        let mut value = Command::new("memcoder");
        value.args(["service", "serve"]);
        value
    };
    command
        .arg("--host")
        .arg("127.0.0.1")
        .arg("--port")
        .arg(port)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    command.spawn().ok()
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            app.manage(ServiceChild(Mutex::new(start_service())));
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building MemCoder Studio")
        .run(|app_handle, event| {
            if let RunEvent::Exit = event {
                if let Ok(mut child) = app_handle.state::<ServiceChild>().0.lock() {
                    if let Some(process) = child.as_mut() {
                        let _ = process.kill();
                    }
                }
            }
        });
}
