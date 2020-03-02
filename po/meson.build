i18n.gettext(
	'parlatype_lo',
	data_dirs: [ '.' ],
	install: false
	# requires meson >= 0.50
	# install_dir: join_paths(extension_dir, 'locale')
)

run_command('install_mo_locally.sh')

if bundled
	install_subdir(
		join_paths(meson.current_build_dir(), 'locale'),
		install_dir: extension_dir,
	)
endif
