extension_dir = join_paths(base_lo_dir, 'share', 'extensions', 'parlatype')
script_dir = join_paths(base_lo_dir, 'share', 'Scripts', 'python')

# description.xml is generated in 3 steps:
# 1) Configure the version
# 2) Merge translations for <display-name>
# 3) Generate <extension-description> links and text files
#    in description/ for en and all translated languages
#    using description_translation.xml and a flaky script

desc = configuration_data()
desc.set('VERSION', meson.project_version())
description_in_in = configure_file(
	input: 'description.xml.in.in.in',
	output: 'description.xml.in.in',
	configuration: desc
)

description_in = i18n.merge_file(
	input: description_in_in,
	output: 'description.xml.in',
	type: 'xml',
	po_dir: '../po',
	data_dirs: [ '../po' ],
	install: false,
)

i18n_script = find_program('i18n_description.sh', required: true)

description = custom_target(
	'description',
	input: description_in,
	output: 'description.xml',
	command: [ i18n_script, meson.project_source_root(), meson.project_build_root() ],
	install: bundled,
	install_dir: extension_dir,
)

subdir('META-INF')
subdir('options')
subdir('toolbar')

if bundled
	subdir('asr')
	subdir('images')
	subdir('python')
	install_subdir(
		join_paths(meson.current_build_dir(), 'description'),
		install_dir: extension_dir,
	)
endif