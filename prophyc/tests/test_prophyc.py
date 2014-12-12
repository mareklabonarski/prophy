import os
import sys
import subprocess

import pytest

main_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

empty_python_output = """\
import prophy
"""

def tr(str_):
    """ Facilitates testing strings output from windows cmd-line programs. """
    return str_.translate(None, '\r')

def call(args):
    popen = subprocess.Popen(["python", "-m", "prophyc"] + args,
                             cwd = main_dir,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE)
    out, err = popen.communicate()
    return popen.returncode, out, err

def test_showing_version():
    ret, out, err = call(["--version"])
    expected_version = '0.4.2'
    assert ret == 0
    assert tr(out) == 'prophyc {}\n'.format(expected_version)
    assert err == ""

def test_missing_input():
    ret, out, err = call([])
    assert ret == 1
    assert out == ""
    assert tr(err) == "prophyc: error: missing input file\n"

def test_no_output_directory(tmpdir_cwd):
    open("input.xml", "w").write("")
    ret, out, err = call(["--python_out", "no_dir",
                          os.path.join(str(tmpdir_cwd), "input_xml")])
    assert ret == 1
    assert out == ""
    assert tr(err) == "prophyc: error: argument --python_out: no_dir directory not found\n"

def test_missing_output(tmpdir_cwd):
    open("input.xml", "w")
    ret, out, err = call(["--isar", os.path.join(str(tmpdir_cwd), "input.xml")])
    assert ret == 1
    assert out == ""
    assert tr(err) == "Missing output directives\n"

def test_passing_isar_and_sack(tmpdir_cwd):
    open("input", "w")
    ret, out, err = call(["--isar", "--sack", "--python_out", ".",
                          os.path.join(str(tmpdir_cwd), "input")])
    assert ret == 1
    assert out == ""
    assert tr(err) == "prophyc: error: argument --sack: not allowed with argument --isar\n"

def test_isar_compiles_single_empty_xml(tmpdir_cwd):
    open("input.xml", "w").write("<struct/>")
    ret, out, err = call(["--isar", "--python_out", str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.xml")])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert empty_python_output == open("input.py").read()

def test_isar_compiles_multiple_empty_xmls(tmpdir_cwd):
    open("input1.xml", "w").write("<struct/>")
    open("input2.xml", "w").write("<struct/>")
    open("input3.xml", "w").write("<struct/>")
    ret, out, err = call(["--isar",
                          "--python_out",
                          str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input1.xml"),
                          os.path.join(str(tmpdir_cwd), "input2.xml"),
                          os.path.join(str(tmpdir_cwd), "input3.xml")])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert empty_python_output == open("input1.py").read()
    assert empty_python_output == open("input2.py").read()
    assert empty_python_output == open("input3.py").read()

def test_outputs_to_correct_directory(tmpdir_cwd):
    open("input.xml", "w").write("<struct/>")
    os.mkdir("output")
    ret, out, err = call(["--isar", "--python_out",
                          os.path.join(str(tmpdir_cwd), "output"),
                          os.path.join(str(tmpdir_cwd), "input.xml")])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert empty_python_output == open(os.path.join("output", "input.py")).read()

def test_isar_patch(tmpdir_cwd):
    open("input.xml", "w").write("""\
<x>
    <struct name="B">
        <member name="a" type="u8"/>
    </struct>
    <struct name="A">
        <member name="a" type="u8"/>
    </struct>
</x>
""")

    open("patch", "w").write("""\
B insert 999 b A
B dynamic b a
""")
    ret, out, err = call(["--isar", "--patch",
                          os.path.join(str(tmpdir_cwd), "patch"),
                          "--python_out",
                          str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.xml")])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert empty_python_output + """\

class A(prophy.struct):
    __metaclass__ = prophy.struct_generator
    _descriptor = [('a', prophy.u8)]

class B(prophy.struct):
    __metaclass__ = prophy.struct_generator
    _descriptor = [('a', prophy.u8),
                   ('b', prophy.array(A, bound = 'a'))]
""" == open("input.py").read()

def test_isar_cpp(tmpdir_cwd):
    open("input.xml", "w").write("""
<xml>
    <struct name="Test">
        <member name="x" type="u32">
            <dimension isVariableSize="true"/>
        </member>
    </struct>
</xml>
""")

    ret, out, err = call(["--isar",
                          "--cpp_out", str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.xml")])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert open("input.pp.hpp").read() == """\
#ifndef _PROPHY_GENERATED_input_HPP
#define _PROPHY_GENERATED_input_HPP

#include <prophy/prophy.hpp>

struct Test
{
    uint32_t x_len;
    uint32_t x[1]; /// dynamic array, size in x_len
};

namespace prophy
{

template <> Test* swap<Test>(Test*);

} // namespace prophy

#endif  /* _PROPHY_GENERATED_input_HPP */
"""
    assert open("input.pp.cpp").read() == """\
#include "input.pp.hpp"

namespace prophy
{

template <>
Test* swap<Test>(Test* payload)
{
    swap(&payload->x_len);
    return cast<Test*>(swap_n_fixed(payload->x, payload->x_len));
}

} // namespace prophy
"""

@pytest.clang_installed
def test_sack_compiles_single_empty_hpp(tmpdir_cwd):
    open("input.hpp", "w").write("")
    ret, out, err = call(["--sack", "--python_out",
                          str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.hpp")])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert empty_python_output == open("input.py").read()

@pytest.clang_installed
def test_sack_patch(tmpdir_cwd):
    open("input.hpp", "w").write("""\
struct X
{
    int x;
};
""")
    open("patch", "w").write("""\
X type x r64
""")
    ret, out, err = call(["--sack", "--patch",
                          os.path.join(str(tmpdir_cwd), "patch"),
                          "--python_out", str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.hpp")])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert empty_python_output + """\

class X(prophy.struct):
    __metaclass__ = prophy.struct_generator
    _descriptor = [('x', prophy.r64)]
""" == open("input.py").read()

@pytest.clang_installed
def test_multiple_outputs(tmpdir_cwd):
    open("input.xml", "w").write("""
<xml>
    <struct name="Test">
        <member name="x" type="u32"/>
    </struct>
</xml>
""")

    ret, out, err = call(["--isar",
                          "--python_out", str(tmpdir_cwd),
                          "--cpp_out", str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.xml")])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert open("input.py").read() == """\
import prophy

class Test(prophy.struct):
    __metaclass__ = prophy.struct_generator
    _descriptor = [('x', prophy.u32)]
"""
    assert open("input.pp.hpp").read() == """\
#ifndef _PROPHY_GENERATED_input_HPP
#define _PROPHY_GENERATED_input_HPP

#include <prophy/prophy.hpp>

struct Test
{
    uint32_t x;
};

namespace prophy
{

template <> Test* swap<Test>(Test*);

} // namespace prophy

#endif  /* _PROPHY_GENERATED_input_HPP */
"""
    assert open("input.pp.cpp").read() == """\
#include "input.pp.hpp"

namespace prophy
{

template <>
Test* swap<Test>(Test* payload)
{
    swap(&payload->x);
    return payload + 1;
}

} // namespace prophy
"""

@pytest.clang_not_installed
def test_clang_not_installed(tmpdir_cwd):
    open("input.hpp", "w").write("")
    ret, out, err = call(["--sack",
                          "--python_out", str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.hpp")])

    assert ret == 1
    assert out == ""
    assert tr(err) == "Sack input requires clang and it's not installed\n"

def test_prophy_language(tmpdir_cwd):
    open("input.prophy", "w").write("""\
struct X
{
    u32 x[5];
    u64 y<2>;
};
union U
{
    1: X x;
    2: u32 y;
};
""")

    ret, out, err = call(["--python_out", str(tmpdir_cwd),
                          "--cpp_out", str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.prophy")])
    assert ret == 0
    assert out == ""
    assert err == ""
    assert open("input.py").read() == """\
import prophy

class X(prophy.struct):
    __metaclass__ = prophy.struct_generator
    _descriptor = [('x', prophy.array(prophy.u32, size = 5)),
                   ('num_of_y', prophy.u32),
                   ('y', prophy.array(prophy.u64, bound = 'num_of_y', size = 2))]

class U(prophy.union):
    __metaclass__ = prophy.union_generator
    _descriptor = [('x', X, 1),
                   ('y', prophy.u32, 2)]
"""
    assert open("input.pp.hpp").read() == """\
#ifndef _PROPHY_GENERATED_input_HPP
#define _PROPHY_GENERATED_input_HPP

#include <prophy/prophy.hpp>

struct X
{
    uint32_t x[5];
    uint32_t num_of_y;
    uint64_t y[2]; /// limited array, size in num_of_y
};

struct U
{
    enum _discriminator
    {
        discriminator_x = 1,
        discriminator_y = 2
    } discriminator;

    union
    {
        X x;
        uint32_t y;
    };
};

namespace prophy
{

template <> X* swap<X>(X*);
template <> U* swap<U>(U*);

} // namespace prophy

#endif  /* _PROPHY_GENERATED_input_HPP */
"""
    assert open("input.pp.cpp").read() == """\
#include "input.pp.hpp"

namespace prophy
{

template <>
X* swap<X>(X* payload)
{
    swap_n_fixed(payload->x, 5);
    swap(&payload->num_of_y);
    swap_n_fixed(payload->y, payload->num_of_y);
    return payload + 1;
}

template <>
U* swap<U>(U* payload)
{
    swap(reinterpret_cast<uint32_t*>(&payload->discriminator));
    switch (payload->discriminator)
    {
        case U::discriminator_x: swap(&payload->x); break;
        case U::discriminator_y: swap(&payload->y); break;
        default: break;
    }
    return payload + 1;
}

} // namespace prophy
"""

def test_prophy_parse_errors(tmpdir_cwd):
    open("input.prophy", "w").write("""\
struct X {};
union Y {};
constant
""")

    ret, out, err = call(["--python_out", str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.prophy")])
    assert ret == 1
    assert out == ""
    assert tr(err) == """\
input.prophy:1:11 error: syntax error at '}'
input.prophy:2:10 error: syntax error at '}'
"""
    assert not os.path.exists("input.py")

def test_cpp_full_out(tmpdir_cwd):
    open("input.prophy", "w").write("""
typedef i16 TP;
const MAX = 4;
struct X {
    u32 x;
    TP y<MAX>;
};
""")

    ret, out, err = call(["--cpp_full_out", str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.prophy")])
    assert ret == 0
    assert out == ""
    assert err == ""

    assert open("input.ppf.hpp").read() == """\
#ifndef _PROPHY_GENERATED_FULL_input_HPP
#define _PROPHY_GENERATED_FULL_input_HPP

#include <stdint.h>
#include <numeric>
#include <vector>
#include <string>
#include <prophy/array.hpp>
#include <prophy/endianness.hpp>
#include <prophy/optional.hpp>
#include <prophy/detail/byte_size.hpp>
#include <prophy/detail/message.hpp>
#include <prophy/detail/mpl.hpp>

namespace prophy
{
namespace generated
{

typedef int16_t TP;

enum { MAX = 4 };

struct X : public prophy::detail::message<X>
{
    enum { encoded_byte_size = 16 };

    uint32_t x;
    std::vector<TP> y; /// limit MAX

    X(): x() { }
    X(uint32_t _1, const std::vector<TP>& _2): x(_1), y(_2) { }

    size_t get_byte_size() const
    {
        return 16;
    }
};

} // namespace generated
} // namespace prophy

#endif  /* _PROPHY_GENERATED_FULL_input_HPP */
"""
    assert open("input.ppf.cpp").read() == """\
#include "input.ppf.hpp"
#include <algorithm>
#include <prophy/detail/encoder.hpp>
#include <prophy/detail/decoder.hpp>
#include <prophy/detail/printer.hpp>
#include <prophy/detail/align.hpp>

using namespace prophy::generated;

namespace prophy
{
namespace detail
{

template <>
template <endianness E>
uint8_t* message_impl<X>::encode(const X& x, uint8_t* pos)
{
    pos = do_encode<E>(pos, x.x);
    pos = do_encode<E>(pos, uint32_t(std::min(x.y.size(), size_t(MAX))));
    do_encode<E>(pos, x.y.data(), uint32_t(std::min(x.y.size(), size_t(MAX))));
    pos = pos + 8;
    return pos;
}
template uint8_t* message_impl<X>::encode<native>(const X& x, uint8_t* pos);
template uint8_t* message_impl<X>::encode<little>(const X& x, uint8_t* pos);
template uint8_t* message_impl<X>::encode<big>(const X& x, uint8_t* pos);

template <>
template <endianness E>
bool message_impl<X>::decode(X& x, const uint8_t*& pos, const uint8_t* end)
{
    return (
        do_decode<E>(x.x, pos, end) &&
        do_decode_resize<E, uint32_t>(x.y, pos, end, MAX) &&
        do_decode_in_place<E>(x.y.data(), x.y.size(), pos, end) &&
        do_decode_advance(8, pos, end)
    );
}
template bool message_impl<X>::decode<native>(X& x, const uint8_t*& pos, const uint8_t* end);
template bool message_impl<X>::decode<little>(X& x, const uint8_t*& pos, const uint8_t* end);
template bool message_impl<X>::decode<big>(X& x, const uint8_t*& pos, const uint8_t* end);

template <>
void message_impl<X>::print(const X& x, std::ostream& out, size_t indent)
{
    do_print(out, indent, "x", x.x);
    do_print(out, indent, "y", x.y.data(), std::min(x.y.size(), size_t(MAX)));
}
template void message_impl<X>::print(const X& x, std::ostream& out, size_t indent);

} // namespace detail
} // namespace prophy
"""

def test_cpp_full_out_error(tmpdir_cwd):
    open("input.xml", "w").write("""
<xml>
    <struct name="Test">
        <member name="x" type="Unknown">
            <dimension isVariableSize="true"/>
        </member>
    </struct>
</xml>
""")

    ret, out, err = call(["--isar", "--cpp_full_out", str(tmpdir_cwd),
                          os.path.join(str(tmpdir_cwd), "input.xml")])
    assert ret == 1
    assert out == ""
    assert tr(err) == "prophyc: error: Test byte size unknown\n"
