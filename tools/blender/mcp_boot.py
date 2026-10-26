# tools/blender/mcp_boot.py — รันภายใน Blender (blender --python …): โหลดปลั๊กอิน MCP จาก $BLENDERMCP_ADDON แล้วเปิดเซิร์ฟเวอร์
# เรียกผ่าน tools/blender/start_blender_mcp.sh เท่านั้น
import importlib.util, os, sys
import bpy

spec = importlib.util.spec_from_file_location("blender_mcp_addon", os.environ["BLENDERMCP_ADDON"])
addon = importlib.util.module_from_spec(spec)
sys.modules["blender_mcp_addon"] = addon
spec.loader.exec_module(addon)
addon.register()
PORT = int(os.environ.get("BLENDER_PORT", "9876"))

def _start():
	scene = getattr(bpy.context, "scene", None)
	if scene is None:
		return 0.5
	server = getattr(bpy.types, "blendermcp_server", None)
	if server is None:
		server = addon.BlenderMCPServer(port=PORT)
		bpy.types.blendermcp_server = server
	if not server.running:
		server.start()
	return None if server.running else 1.0

bpy.app.timers.register(_start, first_interval=1.0, persistent=True)
