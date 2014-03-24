import os
import sys
import subprocess

prophyc_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
prophyc = os.path.join(prophyc_dir, "prophyc.py")

def call(args):
    popen = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = popen.communicate()
    return popen.returncode, out, err

def test_missing_input():
    ret, out, err = call(["python", prophyc])
    assert ret == 1
    assert out == ""
    assert err == "prophyc.py: error: too few arguments\n"

def test_no_output_directory(tmpdir_cwd):
    open("input.xml", "w").write("")
    ret, out, err = call(["python", prophyc, "--python_out", "no_dir", "input.xml"])
    assert ret == 1
    assert out == ""
    assert err == "prophyc.py: error: argument --python_out: no_dir directory not found\n"

# default mode not supported yet, only isar or sack

def test_compiles_single_empty_xml(tmpdir_cwd):
    open("input.xml", "w").write("<struct/>")
    ret, out, err = call(["python", prophyc, "--python_out", ".", "input.xml"])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert "import prophy \n\n\n\n\n\n" == open("input.py").read()

def test_compiles_multiple_empty_xmls(tmpdir_cwd):
    open("input1.xml", "w").write("<struct/>")
    open("input2.xml", "w").write("<struct/>")
    open("input3.xml", "w").write("<struct/>")
    ret, out, err = call(["python", prophyc, "--python_out", ".", "input1.xml", "input2.xml", "input3.xml"])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert "import prophy \n\n\n\n\n\n" == open("input1.py").read()
    assert "import prophy \n\n\n\n\n\n" == open("input2.py").read()
    assert "import prophy \n\n\n\n\n\n" == open("input3.py").read()
