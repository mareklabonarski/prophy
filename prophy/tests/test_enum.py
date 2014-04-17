import prophy
import pytest

class Enumeration(prophy.enum):
    __metaclass__ = prophy.enum_generator
    _enumerators = [("Enumeration_One", 1),
                    ("Enumeration_Two", 2),
                    ("Enumeration_Three", 3)]

class Enumeration8(prophy.enum8):
    __metaclass__ = prophy.enum_generator
    _enumerators = Enumeration._enumerators

class TestEnum():

    class Enum(prophy.struct_packed):
        __metaclass__ = prophy.struct_generator
        _descriptor = [("value", Enumeration)]

    def test_assignment(self):
        x = self.Enum()
        assert x.value == 1
        x.value = "Enumeration_Two"
        assert x.value == 2
        x.value = 3
        assert x.value == 3

        with pytest.raises(Exception):
            x.value = "Enumeration_Four"
        with pytest.raises(Exception):
            x.value = 4

        y = self.Enum()
        assert y.value == 1
        y.copy_from(x)
        assert y.value == 3

    def test_print(self):
        x = self.Enum()
        x.value = 2
        assert str(x) == "value: Enumeration_Two\n"

    def test_encode(self):
        x = self.Enum()
        x.value = 2
        assert x.encode(">") == "\x00\x00\x00\x02"

    def test_decode(self):
        x = self.Enum()
        x.decode("\x00\x00\x00\x02", ">")
        assert x.value == 2

        with pytest.raises(Exception):
            x.decode("\x00\x00\x00\x09", ">")
        with pytest.raises(Exception):
            x.decode("\x00\x00\x01", ">")
        with pytest.raises(Exception):
            x.decode("\x00\x00\x00\x00\x01", ">")

    def test_exceptions(self):
        with pytest.raises(Exception):
            class NoEnumerators(prophy.enum):
                __metaclass__ = prophy.enum_generator
        with pytest.raises(Exception):
            class NamesOverlapping(prophy.enum):
                __metaclass__ = prophy.enum_generator
                _enumerators = [("NamesOverlapping_Overlap", 1),
                                ("NamesOverlapping_Overlap", 2)]
        with pytest.raises(Exception):
            class ValuesOverlapping(prophy.enum):
                __metaclass__ = prophy.enum_generator
                _enumerators = [("ValuesOverlapping_First", 42),
                                ("ValuesOverlapping_Second", 42)]
        with pytest.raises(Exception):
            class ValueOutOfBounds(prophy.enum):
                __metaclass__ = prophy.enum_generator
                _enumerators = [("OutOfBounds", 0xFFFFFFFF + 1)]

class TestEnum8():

    class Enum(prophy.struct_packed):
        __metaclass__ = prophy.struct_generator
        _descriptor = [("value", Enumeration8)]

    def test_assignment(self):
        x = self.Enum()
        assert x.value == 1
        x.value = "Enumeration_Two"
        assert x.value == 2
        x.value = 3
        assert x.value == 3

        with pytest.raises(Exception):
            x.value = "Enumeration_Four"
        with pytest.raises(Exception):
            x.value = 4

        y = self.Enum()
        assert y.value == 1
        y.copy_from(x)
        assert y.value == 3

    def test_print(self):
        x = self.Enum()
        x.value = 2
        assert str(x) == "value: Enumeration_Two\n"

    def test_encode(self):
        x = self.Enum()
        x.value = 2
        assert x.encode(">") == "\x02"

    def test_decode(self):
        x = self.Enum()
        x.decode("\x02", ">")
        assert x.value == 2

        with pytest.raises(Exception):
            x.decode("\x09", ">")
        with pytest.raises(Exception):
            x.decode("", ">")
        with pytest.raises(Exception):
            x.decode("\x00\x01", ">")

    def test_exceptions(self):
        with pytest.raises(Exception):
            class NoEnumerators(prophy.enum8):
                __metaclass__ = prophy.enum_generator

        with pytest.raises(Exception) as e:
            class NamesOverlapping(prophy.enum8):
                __metaclass__ = prophy.enum_generator
                _enumerators = [("NamesOverlapping_Overlap", 1),
                                ("NamesOverlapping_Overlap", 2)]
        assert "names overlap" == e.value.message

        with pytest.raises(Exception) as e:
            class ValuesOverlapping(prophy.enum8):
                __metaclass__ = prophy.enum_generator
                _enumerators = [("ValuesOverlapping_First", 42),
                                ("ValuesOverlapping_Second", 42)]
        assert "values overlap" == e.value.message

        with pytest.raises(Exception) as e:
            class ValueOutOfBounds(prophy.enum8):
                __metaclass__ = prophy.enum_generator
                _enumerators = [("OutOfBounds", 256)]
        assert "out of bounds" == e.value.message

class TestEnumFixedArray():

    class Enum(prophy.struct_packed):
        __metaclass__ = prophy.struct_generator
        _descriptor = [("value", prophy.array(Enumeration, size = 2))]

    def test_assignment(self):
        x = self.Enum()
        assert x.value[:] == [1, 1]
        assert x.value[0] == 1
        assert x.value[1] == 1
        x.value[0] = 2
        x.value[1] = "Enumeration_Two"
        assert x.value[:] == [2, 2]

        y = self.Enum()
        assert y.value[:] == [1, 1]
        y.copy_from(x)
        assert y.value[:] == [2, 2]

    def test_print(self):
        x = self.Enum()
        x.value[:] = [2, 2]
        assert str(x) == ("value: Enumeration_Two\n"
                          "value: Enumeration_Two\n")

    def test_encode(self):
        x = self.Enum()
        x.value[:] = [2, 2]
        assert x.encode(">") == "\x00\x00\x00\x02\x00\x00\x00\x02"

    def test_decode(self):
        x = self.Enum()
        x.decode("\x00\x00\x00\x02\x00\x00\x00\x02", ">")
        assert x.value[0] == 2
        assert x.value[1] == 2

class TestEnumBoundArray():

    class Enum(prophy.struct_packed):
        __metaclass__ = prophy.struct_generator
        _descriptor = [("value_len", prophy.u32),
                       ("value", prophy.array(Enumeration, bound = "value_len"))]

    def test_assignment(self):
        x = self.Enum()
        assert x.value[:] == []
        x.value[:] = [1, "Enumeration_One"]
        assert x.value[:] == [1, 1]
        assert x.value[0] == 1
        assert x.value[1] == 1
        x.value[0] = 2
        x.value[1] = "Enumeration_Two"
        assert x.value[:] == [2, 2]

    def test_print(self):
        x = self.Enum()
        x.value[:] = [2, 2]
        assert str(x) == ("value: Enumeration_Two\n"
                          "value: Enumeration_Two\n")

    def test_encode(self):
        x = self.Enum()
        x.value[:] = [2, 2]
        assert x.encode(">") == "\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x02"

    def test_decode(self):
        x = self.Enum()
        x.decode("\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x02", ">")
        assert x.value[0] == 2
        assert x.value[1] == 2

def test_enum_with_0xFFFFFFFF_value():
    class Enum(prophy.enum):
        __metaclass__ = prophy.enum_generator
        _enumerators = [('Enum_Infinity', 0xFFFFFFFF)]
    class Enclosing(prophy.struct_packed):
        __metaclass__ = prophy.struct_generator
        _descriptor = [("value", Enum)]

    assert Enclosing().value == 0xFFFFFFFF