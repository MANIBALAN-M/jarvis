use serde::{Deserialize, Serialize};
use sysinfo::System;
use tauri::{AppHandle, WebviewWindow};
use tauri_plugin_notification::NotificationExt;

#[derive(Serialize, Deserialize)]
pub struct AppInfo {
    pub name: String,
    pub version: String,
    pub environment: String,
}

#[derive(Serialize, Deserialize)]
pub struct SystemStats {
    pub cpu: f32,
    pub memory: f32,
    pub is_placeholder: bool,
    pub label: String,
}

#[tauri::command]
pub fn toggle_window(window: WebviewWindow) -> Result<(), String> {
    if window.is_visible().unwrap_or(false) {
        window.hide().map_err(|e| e.to_string())?;
    } else {
        window.show().map_err(|e| e.to_string())?;
        window.set_focus().map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[tauri::command]
pub fn get_app_info() -> AppInfo {
    AppInfo {
        name: "JARVIS Desktop Agent".to_string(),
        version: "0.2.0".to_string(),
        environment: "production".to_string(),
    }
}

#[tauri::command]
pub fn show_notification(app: AppHandle, title: String, body: String) -> Result<(), String> {
    app.notification()
        .builder()
        .title(title)
        .body(body)
        .show()
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn get_system_stats() -> SystemStats {
    let mut sys = System::new_all();
    sys.refresh_cpu();
    sys.refresh_memory();

    let cpu = sys.global_cpu_info().cpu_usage();
    let total_mem = sys.total_memory() as f32;
    let used_mem = sys.used_memory() as f32;
    let memory = if total_mem > 0.0 { (used_mem / total_mem) * 100.0 } else { 0.0 };

    SystemStats {
        cpu,
        memory,
        is_placeholder: false,
        label: "Live System Metrics".to_string(),
    }
}

#[tauri::command]
pub fn get_api_token() -> String {
    if let Ok(env_token) = std::env::var("JARVIS_API_AUTH_TOKEN") {
        if !env_token.is_empty() {
            return env_token;
        }
    }

    if let Some(user_dirs) = dirs::home_dir() {
        let creds_path = user_dirs.join(".jarvis").join("credentials.json");
        if let Ok(content) = std::fs::read_to_string(creds_path) {
            if let Ok(v) = serde_json::from_str::<serde_json::Value>(&content) {
                if let Some(token) = v.get("api_auth_token").and_then(|t| t.as_str()) {
                    return token.to_string();
                }
            }
        }
    }

    String::new()
}
