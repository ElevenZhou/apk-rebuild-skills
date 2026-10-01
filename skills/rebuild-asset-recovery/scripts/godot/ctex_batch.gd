extends SceneTree
## 批量回导：<imported_dir> 下全部 .ctex → png、.fontdata → ttf
## 用法：godot --headless -s ctex_batch.gd -- <imported_dir> <out_dir> <report.txt>
## 输出：<out_dir>/textures/*.png、<out_dir>/fonts/*.ttf

var _used_names: Dictionary = {}


func _dst_name(src_file: String, out_ext: String) -> String:
	# "name.png-<md5>.ctex" / "name.png-<md5>.etc2.ctex" / "name.ttf-<md5>.fontdata" → "name.<out_ext>"
	var cut := src_file.rfind("-")
	var base := src_file.substr(0, cut).get_basename() if cut > 0 else src_file.get_basename()
	var final := base + "." + out_ext
	if _used_names.has(final):
		var h := src_file.substr(cut + 1, 6)
		final = base + "_" + h + "." + out_ext
	_used_names[final] = true
	return final


func _init() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 3:
		print("usage: godot --headless -s ctex_batch.gd -- <imported_dir> <out_dir> <report.txt>")
		quit(2)
		return
	var imp: String = args[0].trim_suffix("/") + "/"
	var out: String = args[1].trim_suffix("/") + "/"
	var report: String = args[2]

	var dir := DirAccess.open(imp)
	if dir == null:
		print("FATAL: cannot open ", imp)
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(out + "textures")
	DirAccess.make_dir_recursive_absolute(out + "fonts")
	DirAccess.make_dir_recursive_absolute(report.get_base_dir())

	var lines: PackedStringArray = []
	var ok_ctex := 0
	var fail_ctex := 0
	var ok_font := 0
	var fail_font := 0
	dir.list_dir_begin()
	var fname := dir.get_next()
	while fname != "":
		if not dir.current_is_dir():
			if fname.ends_with(".ctex"):
				var res = ResourceLoader.load(imp + fname)
				var img: Image = null
				if res is Texture2D:
					img = res.get_image()
				elif res is Image:
					img = res
				if img == null or img.is_empty():
					fail_ctex += 1
					lines.append("FAIL\tctex\t%s\t(load/null-image)" % fname)
				else:
					if img.is_compressed():
						img.decompress()
					var dst := out + "textures/" + _dst_name(fname, "png")
					var err := img.save_png(dst)
					if err == OK:
						ok_ctex += 1
						lines.append("OK\tctex\t%s\t-> %s %dx%d" % [fname, dst.get_file(), img.get_width(), img.get_height()])
					else:
						fail_ctex += 1
						lines.append("FAIL\tctex\t%s\t(save err=%d)" % [fname, err])
			elif fname.ends_with(".fontdata"):
				var res = ResourceLoader.load(imp + fname)
				if res is FontFile:
					var dst := out + "fonts/" + _dst_name(fname, "ttf")
					var f := FileAccess.open(dst, FileAccess.WRITE)
					f.store_buffer(res.data)
					f.close()
					ok_font += 1
					lines.append("OK\tfont\t%s\t-> %s %dB" % [fname, dst.get_file(), res.data.size()])
				else:
					fail_font += 1
					lines.append("FAIL\tfont\t%s\t(load)" % fname)
		fname = dir.get_next()
	dir.list_dir_end()

	lines.append("SUMMARY\tctex ok=%d fail=%d\tfont ok=%d fail=%d" % [ok_ctex, fail_ctex, ok_font, fail_font])
	var rf := FileAccess.open(report, FileAccess.WRITE)
	for l in lines:
		rf.store_line(l)
	rf.close()
	print("ctex ok=", ok_ctex, " fail=", fail_ctex, " | font ok=", ok_font, " fail=", fail_font)
	quit(0 if fail_ctex + fail_font == 0 else 1)
