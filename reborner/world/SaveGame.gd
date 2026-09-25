# world/SaveGame.gd — เซฟ/โหลดเป็น JSON อ่านได้ด้วยตา
# ไฟล์อยู่ที่ user:// (Windows: %APPDATA%\Godot\app_userdata\<ชื่อโปรเจกต์>)
class_name SaveGame
extends RefCounted

const PATH := "user://reborner_save.json"

static func save(ps: PlayerState) -> bool:
	var f := FileAccess.open(PATH, FileAccess.WRITE)
	if f == null:
		push_error("บันทึกเกมไม่ได้ (error %d)" % FileAccess.get_open_error())
		return false
	f.store_string(JSON.stringify(ps.to_dict(), "\t"))
	f.close()
	return true

static func load_into(ps: PlayerState) -> bool:
	if not FileAccess.file_exists(PATH):
		return false
	var data = JSON.parse_string(FileAccess.get_file_as_string(PATH))
	if typeof(data) != TYPE_DICTIONARY:
		push_warning("ไฟล์เซฟเสีย — เริ่มเกมใหม่")
		return false
	ps.from_dict(data)
	return true

static func clear() -> void:
	if FileAccess.file_exists(PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(PATH))
