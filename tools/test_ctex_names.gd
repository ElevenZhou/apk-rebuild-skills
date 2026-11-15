extends SceneTree
## Run: godot --headless -s tools/test_ctex_names.gd -- <ctex_batch.gd>
## Exercise the actual naming function without invoking the batch entrypoint.
func _init() -> void:
	var args: PackedStringArray=OS.get_cmdline_user_args()
	if args.size()!=1: quit(2);return
	var source: String=FileAccess.get_file_as_string(args[0])
	var start: int=source.find("func _dst_name(")
	var end: int=source.find("\n\nfunc _init",start)
	if start<0 or end<0: quit(2);return
	var script: GDScript=GDScript.new()
	script.source_code="extends RefCounted\nvar _used_names: Dictionary = {}\n"+source.substr(start,end-start)
	if script.reload()!=OK: quit(2);return
	var names=script.new()
	var outputs: Array=[]
	for filename in ["A.png-abcdef01.ctex","a.png-abcdef02.ctex","A.png-abcdef03.ctex"]:
		outputs.append(names._dst_name(filename,"png").to_lower())
	var unique: Dictionary={}
	for name in outputs: unique[name]=true
	var ok: bool=unique.size()==3 and outputs[2].ends_with("_2.png")
	print(JSON.stringify({"case_insensitive_unique":unique.size(),"short_hash_collision_suffix":outputs[2],"pass":ok}))
	quit(0 if ok else 1)
