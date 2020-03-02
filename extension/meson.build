extension_dir = join_paths(base_lo_dir, 'share', 'extensions', 'parlatype')
script_dir = join_paths(base_lo_dir, 'share', 'Scripts', 'python', 'parlatype')

# description.xml is generated in 3 steps:
# 1) Configure the version
# 2) Generate <extension-description> links and text files
#    in description/ for en and all translated languages
#    using description_translation.xml and a flaky script
# 3) Merge translations for <display-name>

desc = configuration_data()
desc.set('VERSION', meson.project_version())
configure_file(
	input: 'description.xml.in.in.in',
	output: 'description.xml.in.in',
	configuration: desc
)

run_command ('i18n_description.sh')

description = i18n.merge_file(
	input: join_paths(meson.current_build_dir(), 'description.xml.in'),
	output: 'description.xml',
	type: 'xml',
	po_dir: '../po',
	data_dirs: [ '../po' ],
	install: bundled,
	install_dir: extension_dir,
)

subdir('META-INF')
subdir('options')
subdir('toolbar')

if bundled
	subdir('python')

	install_subdir(
		join_paths(meson.current_build_dir(), 'description'),
		install_dir: extension_dir,
	)

	install_subdir(
		'images',
		install_dir: extension_dir
	)
	install_subdir(
		'license',
		install_dir: extension_dir
	)
endif