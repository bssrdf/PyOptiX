import weakref
from pyoptix._driver import NativeContextWrapper
from pyoptix.enums import Exception
from pyoptix.compiler import Compiler
from pyoptix.mixins.scoped import ScopedMixin

_context_stack = []


def current_context():
    return _context_stack[-1]


def _push_context(ctx):
    if not isinstance(ctx, Context):
        raise TypeError('context must be an instance of Context')
    _context_stack.append(ctx)


def _pop_context():
    return _context_stack.pop()


class Context(NativeContextWrapper, ScopedMixin):
    def __init__(self):
        NativeContextWrapper.__init__(self)
        ScopedMixin.__init__(self)
        self._program_cache = {}
        self._miss_programs = {}
        self._destroyables = []

        _push_context(self)

        sm_major, sm_minor = self.get_device_compute_capability(0)
        Compiler.arch = "sm_{0}{1}".format(sm_major, sm_minor)

    def __del__(self):
        for destroyable in self._destroyables:
            if destroyable() is not None:
                destroyable()._set_destroyed()

    @property
    def program_cache(self):
        return self._program_cache

    def push(self):
        if current_context() == self:
            raise RuntimeError("Cannot push: Context is already at the top of the stack")
        else:
            _push_context(self)

    def pop(self):
        if current_context() == self:
            _pop_context()
        else:
            raise RuntimeError("Cannot pop: Context is not at the top of the stack")

    def launch(self, entry_point_index, width, height=None, depth=None):
        if not height:
            self._launch_1d(entry_point_index, width)
        elif not depth:
            self._launch_2d(entry_point_index, width, height)
        else:
            self._launch_3d(entry_point_index, width, height, depth)

    def set_miss_program(self, ray_type_index, program):
        self._miss_programs[ray_type_index] = program
        self._set_miss_program(ray_type_index, program)

    def get_miss_program(self, ray_type_index):
        return self._miss_programs[ray_type_index]

    def set_all_exceptions_enabled(self, is_enabled):
        self.set_exception_enabled(Exception.all, is_enabled)

    def _create_accelerator(self, builder, traverser):
        obj = NativeContextWrapper._create_accelerator(self, builder, traverser)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed Accelerator!")
        return obj

    def _create_geometry(self):
        obj = NativeContextWrapper._create_geometry(self)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed Geometry!")
        return obj

    def _create_buffer(self, buffer_type):
        obj = NativeContextWrapper._create_buffer(self, buffer_type)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed Buffer!")
        return obj

    def _create_geometry_group(self):
        obj = NativeContextWrapper._create_geometry_group(self)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed GeometryGroup!")
        return obj

    def _create_geometry_instance(self):
        obj = NativeContextWrapper._create_geometry_instance(self)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed GeometryInstance!")
        return obj

    def _create_group(self):
        obj = NativeContextWrapper._create_group(self)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed Group!")
        return obj

    def _create_material(self):
        obj = NativeContextWrapper._create_material(self)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed Material!")
        return obj

    def _create_program_from_file(self, file_name, function_name):
        obj = NativeContextWrapper._create_program_from_file(self, file_name, function_name)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed Program!")
        return obj

    def _create_selector(self):
        obj = NativeContextWrapper._create_selector(self)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed Selector!")
        return obj

    def _create_texture_sampler(self):
        obj = NativeContextWrapper._create_texture_sampler(self)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed TextureSampler!")
        return obj

    def _create_transform(self):
        obj = NativeContextWrapper._create_transform(self)
        self._destroyables.append(weakref.ref(obj))
        weakref.finalize(obj, print, "You killed Transform!")
        return obj


# Create a context automatically
Context()
