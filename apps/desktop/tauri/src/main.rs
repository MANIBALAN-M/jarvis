// Prevents additional console window on Windows in release builds, do not remove!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod hotkeys;
mod tray;

use commands::{get_api_token, get_app_info, get_system_stats, show_notification, toggle_window};

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(tauri_plugin_notification::init())
        .setup(|app| {
            let handle = app.handle();
            let _ = tray::setup_tray(handle);
            let _ = hotkeys::setup_hotkeys(handle);
            println!("[JARVIS] Tauri Desktop Shell v0.2.0 initialized.");
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            toggle_window,
            get_app_info,
            show_notification,
            get_system_stats,
            get_api_token
        ])
        .run(tauri::generate_context!())
        .expect("error while running JARVIS tauri application");
}
