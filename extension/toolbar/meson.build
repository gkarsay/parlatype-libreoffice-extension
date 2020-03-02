toolbar = i18n.merge_file(
	input: 'Toolbar.xcu.in',
	output: 'Toolbar.xcu',
	type: 'xml',
	po_dir: '../../po',
	data_dirs: [ '../../po' ],
	install: bundled,
	install_dir: join_paths(extension_dir, 'toolbar')
)

window_state = i18n.merge_file(
	input: 'WriterWindowState.xcu.in',
	output: 'WriterWindowState.xcu',
	type: 'xml',
	po_dir: '../../po',
	data_dirs: [ '../../po' ],
	install: bundled,
	install_dir: join_paths(extension_dir, 'toolbar')
)

if bundled
	install_data(
		[ 'ProtocolHandler.xcu' ],
		install_dir: join_paths(extension_dir, 'toolbar')
	)
endif