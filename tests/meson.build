python = find_program('python3')

test_env = environment()
test_env.prepend('PYTHONPATH', python_utils_dir)

unit_tests = [
	'test_parlatype_utils',
]

foreach test_name: unit_tests
	file = join_paths(meson.current_source_dir(), '@0@.py'.format(test_name))
	test(test_name,
	     python,
	     args: [file],
	     env: test_env,
	     suite: ['unit']
	)
endforeach
