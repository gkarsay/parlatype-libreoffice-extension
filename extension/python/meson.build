# Install Extension
install_subdir(
	'components',
	install_dir: join_paths(extension_dir, 'python')
)

# Install Macros
install_data(
	'macros/Macros.py',
	rename: 'Parlatype.py',
	install_dir: script_dir,
)

# Copy pythonpath from Extension to Macros
install_subdir(
	'components/pythonpath',
	install_dir: script_dir,
)