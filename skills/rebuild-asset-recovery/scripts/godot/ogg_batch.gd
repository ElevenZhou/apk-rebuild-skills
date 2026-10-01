extends SceneTree
## 批量回导：<imported_dir> 下全部 .oggvorbisstr → 标准 .ogg（OggPacketSequence 重封装 + 回读校验）
## 用法：godot --headless -s ogg_batch.gd -- <imported_dir> <out_dir> <report.txt>

const SERIAL := 0x52424C44  # 任意固定流序号

var _table := PackedInt32Array()
var _used_names: Dictionary = {}


func _crc_table() -> PackedInt32Array:
	if _table.is_empty():
		_table.resize(256)
		for i in 256:
			var r: int = i << 24
			for j in 8:
				r = ((r << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if (r & 0x80000000) else (r << 1) & 0xFFFFFFFF
			_table[i] = r
	return _table


func _ogg_crc32(data: PackedByteArray) -> int:
	# MSB-first, init=0, no xorout；索引必须用移位前的高字节
	var crc := 0
	var t := _crc_table()
	for byte in data:
		var idx := ((crc >> 24) ^ byte) & 0xFF
		crc = ((crc << 8) & 0xFFFFFFFF) ^ (t[idx] & 0xFFFFFFFF)
	return crc


func _u32(v: int) -> PackedByteArray:
	var b := PackedByteArray()
	b.resize(4)
	b.encode_u32(0, v & 0xFFFFFFFF)
	return b


func _u64(v: int) -> PackedByteArray:
	var b := PackedByteArray()
	b.resize(8)
	b.encode_u64(0, v)
	return b


func _make_page(packets: Array, seq: int, granule: int, bos: bool, eos: bool) -> PackedByteArray:
	var segs := PackedByteArray()
	var body := PackedByteArray()
	for pkt: PackedByteArray in packets:
		var n := pkt.size()
		for j in n / 255:
			segs.append(255)
		segs.append(n % 255)  # 255 整数倍时这里补 0 段
		body.append_array(pkt)
	var page := PackedByteArray()
	page.append_array("OggS".to_ascii_buffer())
	page.append(0)
	page.append((2 if bos else 0) | (4 if eos else 0))
	page.append_array(_u64(granule))
	page.append_array(_u32(SERIAL))
	page.append_array(_u32(seq))
	page.append_array(_u32(0))
	page.append(segs.size())
	page.append_array(segs)
	page.append_array(body)
	page.encode_u32(22, _ogg_crc32(page))
	return page


func _dst_name(src_file: String) -> String:
	# "name.ogg-<md5>.oggvorbisstr" → "name.ogg"
	var cut := src_file.rfind("-")
	var base := (src_file.substr(0, cut).get_basename() if cut > 0 else src_file.get_basename()) + ".ogg"
	if _used_names.has(base):
		base = base.get_basename() + "_" + src_file.substr(cut + 1, 6) + ".ogg"
	_used_names[base] = true
	return base


func _init() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 3:
		print("usage: godot --headless -s ogg_batch.gd -- <imported_dir> <out_dir> <report.txt>")
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
	DirAccess.make_dir_recursive_absolute(out)
	DirAccess.make_dir_recursive_absolute(report.get_base_dir())

	var lines: PackedStringArray = []
	var ok := 0
	var fail := 0
	dir.list_dir_begin()
	var fname := dir.get_next()
	while fname != "":
		if not dir.current_is_dir() and fname.ends_with(".oggvorbisstr"):
			var res = ResourceLoader.load(imp + fname)
			if res is AudioStreamOggVorbis:
				var ps: OggPacketSequence = res.packet_sequence
				var pages: Array = ps.packet_data
				var granules: PackedInt64Array = ps.granule_positions
				var buf := PackedByteArray()
				for i in pages.size():
					var g: int = granules[mini(i, granules.size() - 1)]
					buf.append_array(_make_page(pages[i], i, g, i == 0, i == pages.size() - 1))
				var dst := out + _dst_name(fname)
				var f := FileAccess.open(dst, FileAccess.WRITE)
				f.store_buffer(buf)
				f.close()
				var back := AudioStreamOggVorbis.load_from_buffer(buf)
				if back != null and absf(back.get_length() - res.get_length()) < 0.05:
					ok += 1
					lines.append("OK\togg\t%s\t-> %s %.2fs" % [fname, dst.get_file(), res.get_length()])
				else:
					fail += 1
					lines.append("FAIL\togg\t%s\t(roundtrip mismatch)" % fname)
			else:
				fail += 1
				lines.append("FAIL\togg\t%s\t(load)" % fname)
		fname = dir.get_next()
	dir.list_dir_end()

	lines.append("SUMMARY\togg ok=%d fail=%d" % [ok, fail])
	var rf := FileAccess.open(report, FileAccess.WRITE)
	for l in lines:
		rf.store_line(l)
	rf.close()
	print("ogg ok=", ok, " fail=", fail)
	quit(0 if fail == 0 else 1)
