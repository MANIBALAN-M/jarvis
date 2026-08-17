use tauri::{
    menu::{Menu, MenuItem},
    tray::TrayIconBuilder,
    AppHandle, Manager,
};

pub fn setup_tray(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let show_hide = MenuItem::with_id(app, "toggle", "Show / Hide JARVIS", true, None::<&str>)?;
    let status = MenuItem::with_id(app, "status", "Status: Online (127.0.0.1:8765)", false, None::<&str>)?;
    let quit = MenuItem::with_id(app, "quit", "Quit JARVIS", true, None::<&str>)?;

    let menu = Menu::with_items(app, &[&status, &show_hide, &quit])?;

    let _tray = TrayIconBuilder::new()
        .menu(&menu)
        .on_menu_event(|app, event| match event.id.as_ref() {
            "toggle" => {
                if let Some(window) = app.get_webview_window("main") {
                    if window.is_visible().unwrap_or(false) {
                        let _ = window.hide();
                    } else {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
            }
            "quit" => {
                app.exit(0);
            }
            _ => {}
        })
        .build(app)?;

    Ok(())
}
