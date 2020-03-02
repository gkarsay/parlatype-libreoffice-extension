datadir = get_option('datadir')
appdatadir = join_paths(prefix, datadir, 'metainfo')

metainfo = app_id + '.metainfo.xml'
i18n.merge_file(
	input: metainfo + '.in',
	output: metainfo,
	type: 'xml',
	po_dir: '../po',
	install: true,
	install_dir: appdatadir
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
	test('Validating ' + metainfo,
		appstream_util,
		args: ['validate-relax', '--nonet', metainfo],
		workdir: meson.current_build_dir()
	)
endif