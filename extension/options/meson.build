options_dialog = i18n.merge_file(
	input: 'OptionsDialogRegistry.xcu.in',
	output: 'OptionsDialogRegistry.xcu',
	type: 'xml',
	po_dir: '../../po',
	data_dirs: [ '../../po' ],
	install: bundled,
	install_dir: join_paths(extension_dir, 'options')
)

if bundled
	install_data(
		[ 'ConfigurationData.xcu', \
		  'ConfigurationSchema.xcs', \
		  'OptionsDialogPage.xdl' ],
		install_dir: join_paths(extension_dir, 'options')
	)
endif