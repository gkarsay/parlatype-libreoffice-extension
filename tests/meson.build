python = find_program('python3')

testpaths = [
	python_dir,                     # files to be tested
	python_utils_dir,		# files to be tested
	meson.current_source_dir(),	# tests (unittest can't import paths)
]

test_env = environment()
test_env.prepend('PYTHONPATH', testpaths)

unit_tests = [
	'test_parlatype_utils',
	'test_document_link',
]

foreach test_name: unit_tests
	test(test_name,
	     python,
	     args: ['-m', 'unittest', '-v', test_name],
	     env: test_env,
	     # test_parlatype_utils fails if parallel
	     is_parallel: false,
	     suite: ['unit']
	)
endforeach
