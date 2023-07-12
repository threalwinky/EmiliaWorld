from module.lib import *

def write_file(code, input, code_file, input_file):
    f = open(code_file, "w")
    f.write(code)
    f.close()
    f = open(input_file, "w")
    f.write(input)
    f.close()

def run_code(language, code, input):
    res = "None of language is used"
    if (language == "python"):
        write_file(code, input, "code_runner/python/code.py", "code_runner/python/input.py")
        try:
            output = subprocess.check_output(
                "python code_runner/python/code.py < code_runner/python/input.py", stderr=subprocess.STDOUT, shell=True, timeout=3,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            res = exc.output
        else:
            res = output
    elif (language == "c"):
        write_file(code, input, "code_runner/c/code.c", "code_runner/c/input.c")
        try:
            output = subprocess.check_output(
                "gcc code_runner/c/code.c -o code_runner/c/code.exe", stderr=subprocess.STDOUT, shell=True, timeout=3,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            res = exc.output
        else:
            output = subprocess.check_output(
                "cd code_runner/c && (code.exe < input.c)", stderr=subprocess.STDOUT, shell=True, timeout=3,
                universal_newlines=True)
            res = output
    elif (language == "cpp"):
        write_file(code, input, "code_runner/cpp/code.cpp", "code_runner/cpp/input.cpp")
        try:
            output = subprocess.check_output(
                "g++ code_runner/cpp/code.cpp -o code_runner/cpp/code.exe", stderr=subprocess.STDOUT, shell=True, timeout=3,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            res = exc.output
        else:
            output = subprocess.check_output(
                "cd code_runner/cpp && (code.exe < input.cpp)", stderr=subprocess.STDOUT, shell=True, timeout=3,
                universal_newlines=True)
            res = output
    elif (language == "javascript"):
        write_file(code, input, "code_runner/javascript/code.js", "code_runner/javascript/input.js")
        try:
            output = subprocess.check_output(
                "node code_runner/javascript/code.js < code_runner/javascript/input.js", stderr=subprocess.STDOUT, shell=True, timeout=3,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            res = exc.output
        else:
            res = output
    if (language == "golang"):
        write_file(code, input, "code_runner/golang/code.go", "code_runner/golang/input.go")
        try:
            output = subprocess.check_output(
                "go run code_runner/golang/code.go < code_runner/golang/input.go", stderr=subprocess.STDOUT, shell=True, timeout=3,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            res = exc.output
        else:
            res = output
    return res