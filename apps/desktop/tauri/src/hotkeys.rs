use tauri::{AppHandle, Manager};
use tauri_plugin_global_shortcut::{GlobalShortcutExt, Shortcut, ShortcutState};

pub fn setup_hotkeys(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    println!("[JARVIS Hotkeys] Registering global shortcut listeners (Ctrl+Space)...");
    let shortcut: Shortcut = "Ctrl+Space".parse()?;
    
    let _ = app.global_shortcut().on_shortcut(shortcut, move |app_handle, _shortcut, event| {
        if event.state() == ShortcutState::Pressed {
            if let Some(window) = app_handle.get_webview_window("main") {
                if window.is_visible().unwrap_or(false) {
                    let _ = window.hide();
                } else {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        }
    });

    Ok(())
}
