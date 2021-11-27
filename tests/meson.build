python = find_program('python3')

testpaths = [
	python_utils_dir,		# files to be tested
	meson.current_source_dir(),	# tests (unittest can't import paths)
]

test_env = environment()
test_env.prepend('PYTHONPATH', testpaths)

unit_tests = [
	'test_parlatype_utils',
]

foreach test_name: unit_tests
	test(test_name,
	     python,
	     args: ['-m', 'unittest', '-v', test_name],
	     env: test_env,
	     suite: ['unit']
	)
endforeach